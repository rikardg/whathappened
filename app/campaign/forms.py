from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SelectField
from wtforms.compat import text_type, iteritems
from markupsafe import escape, Markup
from wtforms import SubmitField
from wtforms import widgets
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.fields.core import IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Email
from flask_login import current_user
from wtforms.widgets.core import HiddenInput, Select, TextArea


from .models import HandoutStatus


class CreateForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Create')


class EditForm(CreateForm):
    id = IntegerField(widget=HiddenInput())
    description = StringField('Description', widget=TextArea())
    submit = SubmitField('Save')


class InvitePlayerForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),  Email()])
    submit = SubmitField('Invite')


def available_characters():
    return current_user.profile.characters


class AddCharacterForm(FlaskForm):
    character = QuerySelectField(query_factory=available_characters,
                                 get_label=lambda x: x.title)
    submit = SubmitField('Add character')


class RemoveCharacterForm(FlaskForm):
    id = IntegerField(widget=HiddenInput())
    character = IntegerField(widget=HiddenInput())
    submit = SubmitField('Remove character')


class RemovePlayerForm(FlaskForm):
    id = IntegerField(widget=HiddenInput())
    player = IntegerField(widget=HiddenInput())
    submit = SubmitField('Remove player')


class JoinCampaignForm(FlaskForm):
    invite_code = HiddenField('Invite', validators=[DataRequired()])
    submit = SubmitField('Join campaign')


class EnumField(SelectField):
    def process_data(self, value):
        if value is not None:
            value = value.name
        super(EnumField, self).process_data(value)


class PlayerListField(QuerySelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class HandoutForm(FlaskForm):
    campaign_id = IntegerField(widget=HiddenInput(),
                               validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', widget=TextArea())
    status = EnumField('Status',
                       choices=[(e.name, e.value) for e in HandoutStatus],
                       default=HandoutStatus.draft)

    # players = PlayerListField('Show to', choices=[], coerce=int)
    # players = PlayerListField('Show to', get_label=lambda x: x.user.username)
    submit = SubmitField('Save handout')


class DeleteHandoutForm(FlaskForm):
    campaign_id = IntegerField(widget=HiddenInput(),
                               validators=[DataRequired()])
    id = IntegerField(widget=HiddenInput(),
                      validators=[DataRequired()])
    submit = SubmitField('Delete handout')


class TableRowWidget(object):
    def __init__(self, with_tr_tag=True):
        self.with_tr_tag = with_tr_tag

    def __call__(self, field, **kwargs):
        html = []
        if self.with_tr_tag:
            kwargs.setdefault('id', field.id)
            html.append('<tr %s>' % widgets.core.html_params(**kwargs))

        hidden = ''
        for subfield in field:
            if subfield.type in ('HiddenField', 'CSRFTokenField'):
                hidden += text_type(subfield)
            else:
                html.append('<td>%s%s</td>' % (hidden, text_type(subfield)))
                hidden = ''
        if self.with_tr_tag:
            html.append('</tr>')
        if hidden:
            html.append(hidden)
        return Markup(''.join(html))


class PlayerField(SelectMultipleField):
    widget = TableRowWidget(with_tr_tag=False)
    option_widget = widgets.CheckboxInput()


class RevealHandout(FlaskForm):
    campaign_id = IntegerField(widget=HiddenInput(),
                               validators=[DataRequired()])
    id = IntegerField(widget=HiddenInput(),
                      validators=[DataRequired()])
    players = QuerySelectMultipleField('Show to',
                                       get_label=lambda x: x.user.username)