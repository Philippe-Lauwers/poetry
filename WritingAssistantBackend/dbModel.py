# point to the app.py file and import the db variable from there
# circular import with app.py -> use .extensions instead
from .extensions import db
from sqlalchemy.orm import synonym  # to allow use of synonyms for Columns
from datetime import datetime, timezone  # needed for timestamps

"""
 NOTE:
 * class names and table names can be decoupled e.g.:
class ZIP(db.Model):
    __tablename__ = 'postalCodes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    postalCode = db.Column(db.Integer)
* a table can be linked to more than one class:
postalCodes = Table('postalCodes', metadata,
                    db.Column('id', db.Integer, primary_key=True, autoincrement=True),)
class postalCodes(db.Model):
    __table__ = postalCodes
class ZIP(db.Model):
    __table__ = postalCodes
"""


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_users'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)


class ConfigurationCategory(db.Model):
    __tablename__ = 'configurationCategories'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_configurationCategories'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    configurationCategory = db.Column(db.String(100), nullable=False)


class ConfigurationParameter(db.Model):
    __tablename__ = 'configurationParameters'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_configurationParameters'),
                      db.UniqueConstraint('poemLanguage_id', 'configurationCategory_id', 'parameter',
                                          name='uq_configurationParameters_poemLanguage_category_parameter'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poemLanguage_id = db.Column(db.Integer, db.ForeignKey('poemLanguages.id',
                                                          name='fk_configurationParameters_poemLanguages_id'),
                                nullable=False)
    configurationCategory_id = db.Column(db.Integer, db.ForeignKey('configurationCategories.id',
                                                                   name='fk_configurationParameters_configurationCategories_id'),
                                         nullable=False)
    parameter = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(100), nullable=False)


class PoemLanguage(db.Model):
    __tablename__ = 'poemLanguages'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_poemLanguages'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    language = db.Column(db.String(5), nullable=False)


# For defining the different types of poems. Rhymeschemes are used to group the rhymescheme elements
class RhymeScheme(db.Model):
    __tablename__ = 'rhymeSchemes'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_rhymeSchemes'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rhymeScheme = db.Column(db.String(50), nullable=False)


# The elements in a rhymeScheme
class RhymeSchemeElement(db.Model):
    __tablename__ = 'rhymeSchemeElements'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_rhymeSchemeElements'),
                      db.UniqueConstraint('rhymeScheme_id', 'poemLanguage_id', 'order',
                                          name='uq_rhymeSchemeElements_rhymeScheme_poemLanguage_order'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rhymeScheme_id = db.Column(db.Integer, db.ForeignKey('rhymeSchemes.id',
                                                         name='fk_rhymeSchemeElements_rhymeSchemes_id'), nullable=False)
    poemLanguage_id = db.Column(db.Integer, db.ForeignKey('poemLanguages.id',
                                                          name='fk_rhymeSchemeElements_poemLanguages_id'),
                                nullable=False)
    order = db.Column(db.Integer, nullable=False)
    rhymeSchemeElement = db.Column(db.String(1), nullable=False)
    rhyme = synonym('rhymeSchemeElement')

    # For defining the different themes for poems (will be loaded with the nmf data)


class Theme(db.Model):
    __tablename__ = 'themes'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_themes'),
                      db.UniqueConstraint('poemLanguage_id', 'nmfDim', name='uq_themes_poemLanguage_nmfDim'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poemLanguage_id = db.Column(db.Integer, db.ForeignKey('poemLanguages.id',
                                                          name='fk_themes_poemLanguages_id'), nullable=False)
    nmfDim = db.Column(db.Integer, nullable=False)


# Each theme has three describing words
class ThemeDescriptor(db.Model):
    __tablename__ = 'themeDescriptors'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_themeDescriptors'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('themes.id', name='fk_themeDescriptors_themes_id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    themeDescriptor = db.Column(db.String(100), nullable=False)


class ActionTargetType(db.Model):
    __tablename__ = 'actionTargetTypes'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_actionTargetTypes'),
                      db.UniqueConstraint('actionTargetType', name='uq_actiontargettpyes_actiontargettype'),)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    actionTargetType = db.Column(db.String(100), nullable=False)
    actionTargetTypeDescription = db.Column(db.String(1000), nullable=False)


class ActionTarget(db.Model):
    __tablename__ = 'actionTargets'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_actionTargets'),)

    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(
        db.Integer,
        db.ForeignKey('actions.id', name='fk_actionTargets_actions_id'),
        nullable=False
    )
    actionTargetType_id = db.Column(
        db.Integer,
        db.ForeignKey('actionTargetTypes.id', name='fk_actionTargets_actionTargetTypes_id'),
        nullable=False
    )
    target_id = db.Column(db.Integer, nullable=False)

    # ORM relationships:
    action = db.relationship("Action", back_populates="targets")
    target_type = db.relationship("ActionTargetType")


class ActionType(db.Model):
    __tablename__ = 'actionTypes'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_actionTypes'),
                      db.UniqueConstraint('actionType', name='uq_actiontypes_actiontype'),)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    actionType = db.Column(db.String(100), nullable=False)
    actionTypeDescription = db.Column(db.String(1000), nullable=False)


class Action(db.Model):
    __tablename__ = 'actions'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_actions'),)

    id = db.Column(db.Integer, primary_key=True)
    actionType_id = db.Column(
        db.Integer,
        db.ForeignKey('actionTypes.id', name='fk_actions_actionTypes_id'),
        nullable=False
    )
    timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now()
    )
    targets = db.relationship(
        "ActionTarget",
        back_populates="action",
        cascade="all, delete-orphan"
    )


class Poem(db.Model):
    __tablename__ = 'poems'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_poems'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_poems_user_id'), nullable=False)
    poemLanguage_id = db.Column(db.Integer, db.ForeignKey('poemLanguages.id', name='fk_poems_poemLanguages_id'),
                                nullable=False)
    language = synonym('poemLanguage_id')
    theme_id = db.Column(db.Integer, db.ForeignKey('themes.id', name='fk_poems_themes_id'), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(1000), nullable=True)


class Stanza(db.Model):
    __tablename__ = 'stanzas'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_stanzas'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id', name='fk_stanzas_poems_id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)


class Verse(db.Model):
    __tablename__ = 'verses'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_verses'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stanza_id = db.Column(db.Integer, db.ForeignKey('stanzas.id', name='fk_verses_stanzas_id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    verse = db.Column(db.String(1000), nullable=False)


class Keyword(db.Model):
    __tablename__ = 'keywords'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_keywords'),)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id', name='fk_keywords_poem_id'), nullable=False)
    keyword = db.Column(db.String(100), nullable=False)
