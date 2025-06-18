from datetime import datetime # needed for timestamps
# point to the app.py file and import the db variable from there
# circular import with app.py -> use .extensions instead
from sqlalchemy.sql.schema import UniqueConstraint

from .app import db
from .extensions import db
from sqlalchemy.orm import synonym  # to allow use of synonyms for Columns
import sqlite3

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


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)


class PoemLanguages(db.Model):
    __tablename__ = 'poemLanguages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    language = db.Column(db.String(5), nullable=False)


# For defining the different types of poems. Rhymeschems are used to group the rhymescheme elements
class RhymeSchemes(db.Model):
    __tablename__ = 'rhymeSchemes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rhymeScheme = db.Column(db.String(50), nullable=False)


# The elements in a rhymeScheme
class RhymeSchemeElements(db.Model):
    __tablename__ = 'rhymeSchemeElements'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rhymeScheme_id = db.Column(db.Integer, db.ForeignKey('rhymeSchemes.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    rhymeSchemeElement = db.Column(db.String(1), nullable=False)
    rhyme = synonym('rhymeSchemeElement')


# For defining the different themes for poems (will be loaded with the nmf data)
class Themes(db.Model):
    __tablename__ = 'themes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nmfDim = db.Column(db.Integer, nullable=False)


# Each theme has three describing words
class ThemeDescriptors(db.Model):
    __tablename__ = 'themeDescriptors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('themes.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    descriptor = db.Column(db.String(100), nullable=False)


class Actions(db.Model):
    __tablename__ = 'actions'
    __table_args__ = (db.UniqueConstraint('action', name='uq_actions_action'),)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime,
                          nullable=False,
                          default=datetime.utcnow,
                          server_default=db.func.now())
    UniqueConstraint('action')


class Poems(db.Model):
    __tablename__ = 'poems'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    poemLanguage_id = db.Column(db.Integer, db.ForeignKey('poemLanguages.id'), nullable=False)
    language = synonym('poemLanguage_id')
    theme = db.Column(db.Integer, db.ForeignKey('themes.id'), nullable=False)
    action = db.Column(db.Integer, db.ForeignKey('actions.id'), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(1000), nullable=False)


class Stanzas(db.Model):
    __tablename__ = 'stanzas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id'), nullable=False)
    action = db.Column(db.Integer, db.ForeignKey('actions.id'), nullable=False)

    order = db.Column(db.Integer, nullable=False)


class Verses(db.Model):
    __tablename__ = 'verses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stanza_id = db.Column(db.Integer, db.ForeignKey('stanzas.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    action = db.Column(db.Integer, db.ForeignKey('actions.id'), nullable=False)

    status = db.Column(db.Integer, nullable=False)
    verse = db.Column(db.String(1000), nullable=False)


class Keywords(db.Model):
    __table_name__ = 'keywords'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id'), nullable=False)
    keyword = db.Column(db.String(100), nullable=False)
