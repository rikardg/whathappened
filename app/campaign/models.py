import enum
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Text
from sqlalchemy import Enum
from sqlalchemy.orm import relationship, backref
from app.database import Base


campaign_players = Table('campaign_players',
                            Base.metadata,
                            Column('player_id',
                                      Integer,
                                      ForeignKey('user_profile.id'),
                                      primary_key=True),
                            Column('campaign_id',
                                      Integer,
                                      ForeignKey('campaign.id'),
                                      primary_key=True))

campaign_characters = Table('campaign_characters',
                            Base.metadata,
                               Column('character_id',
                                         Integer,
                                         ForeignKey('charactersheet.id'),
                                         primary_key=True),
                               Column('campaign_id',
                                         Integer,
                                         ForeignKey('campaign.id'),
                                         primary_key=True))


class Campaign(Base):
    __tablename__ = 'campaign'
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    description = Column(Text)
    user_id = Column(Integer, ForeignKey('user_profile.id'))
    user = relationship("UserProfile", back_populates='campaigns')
    players = relationship('UserProfile',
                              secondary=campaign_players,
                              lazy='dynamic',
                              backref=backref('campaigns_as_player',
                                                 lazy=True))
    characters = relationship('Character',
                                 secondary=campaign_characters,
                                 lazy='dynamic',
                                 backref=backref('campaigns', lazy=True))

    handouts = relationship("Handout",
                               back_populates='campaign',
                               lazy='dynamic')

    handout_groups = relationship("HandoutGroup",
                                     back_populates='campaign',
                                     lazy='dynamic')

    @property
    def players_by_id(self):
        return dict((player.id, player) for player in self.players)

    def __repr__(self):
        return '<Campaign {}>'.format(self.title)


player_handouts = Table('campaign_handouts_to_players',
                            Base.metadata,
                           Column('handout_id',
                                     Integer,
                                     ForeignKey('campaign_handout.id'),
                                     primary_key=True),
                           Column('player_id',
                                     Integer,
                                     ForeignKey('user_profile.id'),
                                     primary_key=True))


class HandoutStatus(enum.Enum):
    draft = "Draft"
    deleted = "Deleted"
    hidden = "Hidden"
    visible = "Visible"


class HandoutGroup(Base):
    __tablename__ = 'campaign_handout_group'
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    campaign_id = Column(Integer, ForeignKey('campaign.id'))
    campaign = relationship("Campaign", back_populates='handout_groups')
    handouts = relationship('Handout',
                               lazy='dynamic',
                               back_populates='group')

    def __repr__(self):
        return f'<Handout Group {self.name}>'


class Handout(Base):
    __tablename__ = 'campaign_handout'
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    content = Column(Text)
    campaign_id = Column(Integer, ForeignKey('campaign.id'))
    campaign = relationship("Campaign", back_populates='handouts')
    status = Column('status',
                       Enum(HandoutStatus),
                       default=HandoutStatus.draft)

    players = relationship('UserProfile',
                              secondary=player_handouts,
                              lazy='dynamic',
                              backref=backref('campaign_handouts',
                                                 lazy=True))

    group_id = Column(Integer,
                         ForeignKey('campaign_handout_group.id'),
                         name="group_id")

    group = relationship('HandoutGroup')

    def __repr__(self):
        return '<Handout {}>'.format(self.title)
