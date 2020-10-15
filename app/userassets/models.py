import os
import uuid
import logging

from flask import url_for, current_app
from sqlalchemy import event
from app import db
from app.models import GUID
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


class Asset(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    filename = db.Column(db.String(128))
    owner_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
    owner = db.relationship('UserProfile', backref='assets')
    folder_id = db.Column(GUID(), db.ForeignKey('asset_folder.id'))
    folder = db.relationship('AssetFolder', back_populates='files')

    def __init__(self, *args, **kwargs):
        super(Asset, self).__init__(*args, **kwargs)
        self.loaded = False
        self.data = None

    @property
    def path(self):
        return os.path.join(self.folder.get_path(), self.filename)

    @property
    def url(self):
        return url_for('userassets.view',
                       fileid=self.id,
                       filename=self.filename)

    @property
    def system_path(self):
        return os.path.join(self.folder.system_path,
                            secure_filename(self.filename))


@event.listens_for(Asset, 'before_delete')
def before_asset_delete(mapper, connection, target):
    logger.debug("Asset is being deleted")
    logger.debug(target.filename)
    system_folder = current_app.config['UPLOAD_PATH']
    filepath = target.folder.get_path()
    assetname = secure_filename(target.filename)
    logger.debug(f"Deleting file from {filepath}, {assetname}")
    full_dir = os.path.join(system_folder, filepath)
    full_file_path = os.path.join(full_dir, assetname)
    if os.path.isfile(full_file_path):
        logger.debug("Delete the actual file")
        os.unlink(full_file_path)


class AssetFolder(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
    owner = db.relationship("UserProfile", backref=db.backref('assetfolders', lazy='dynamic'))
    parent_id = db.Column(GUID(),
                          db.ForeignKey('asset_folder.id'),
                          default=None)
    subfolders = db.relationship('AssetFolder', backref=db.backref('parent', remote_side=[id]))
    title = db.Column(db.String(128))
    files = db.relationship("Asset", back_populates='folder')

    def get_path(self):
        if self.parent:
            parent = self.parent.get_path()
            return os.path.join(parent, secure_filename(self.title))
        else:
            return os.path.join(str(self.id), secure_filename(self.title))

    @property
    def path(self):
        if self.parent:
            parent = self.parent.path
            return os.path.join(parent, self.title)
        else:
            return self.title

    @property
    def system_path(self):
        return os.path.join(current_app.config['UPLOAD_PATH'],
                            self.get_path())