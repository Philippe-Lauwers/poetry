# point to the app.py file and import the db variable from there
# circular import with app.py -> use .extensions instead
import random
import string
from datetime import datetime, timezone  # needed for timestamps

from flask_login import UserMixin
from sqlalchemy.orm import synonym  # to allow use of synonyms for Columns

from .extensions import db

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


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_users'),
                        db.UniqueConstraint('email', name='uq_users_email'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        """Set the password hash for the user."""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        """Check the password against the stored hash."""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)


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
    label = db.Column(db.String(100), nullable=False)


class PoemStatus(db.Model):
    __tablename__ = 'poemStatuses'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_poemStatuses'),
                      db.UniqueConstraint('poemStatusNo', name='uq_poemStatuses_poemStatusNo'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poemStatusNo = db.Column(db.Integer, nullable=False)
    poemStatus = db.Column(db.String(100), nullable=False)

# For defining the different types of poems. Rhymeschemes are used to group the rhymescheme elements
class RhymeScheme(db.Model):
    __tablename__ = 'rhymeSchemes'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_rhymeSchemes'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    persistent = db.Column(db.Boolean, nullable=False, default=False)
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
    group_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'actions.id',
            name='fk_actions_actions_group_id',
            ondelete='CASCADE'
        ),
        nullable=True
    )
    targets = db.relationship(
        "ActionTarget",
        back_populates="action",
        cascade="all, delete-orphan"
    )
    parent = db.relationship(
        'Action',
        remote_side=[id],
        backref=db.backref('children', cascade='all, delete-orphan'),
        foreign_keys=[group_id],
    )

def random_string(n=16):
    """Generate a random string of fixed length n."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))
class Poem(db.Model):
    __tablename__ = 'poems'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_poems'),
                      db.UniqueConstraint('user_id', 'lookupKey', name='uq_poems_user_lookupKey'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_poems_user_id'), nullable=False)
    poemLanguage_id = db.Column(db.Integer, db.ForeignKey('poemLanguages.id', name='fk_poems_poemLanguages_id'),
                                nullable=False)
    rhymeScheme_id = db.Column(db.Integer, db.ForeignKey('rhymeSchemes.id', name='fk_poems_rhymeSchemes_id'),
                               nullable=False)
    language = synonym('poemLanguage_id')
    theme_id = db.Column(db.Integer, db.ForeignKey('themes.id', name='fk_poems_themes_id'), nullable=False)
    status = db.Column(db.Integer, db.ForeignKey('poemStatuses.id', name='fk_poems_poemStatuses_id'), nullable=False)
    lookupKey = db.Column(db.String(16), default=lambda:random_string(16), nullable=False)
    poemText = db.Column(db.Text, nullable=True)
    title = db.Column(db.String(1000))

class PreviousPoem(db.Model):
    __tablename__ = 'previousPoems'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_previousPoems'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id', name='fk_previousPoems_poems_id'), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id', name='fk_previousPoems_actions_id'), nullable=False)
    previousTitle = db.Column(db.String(500))
    previousRhymeScheme_id = db.Column(db.Integer, db.ForeignKey('rhymeSchemes.id', name='fk_previousPoems_rhymeSchemes_id'), nullable = False)
    previousTheme_id = db.Column(db.Integer, db.ForeignKey('themes.id', name='fk_previousPoems_themes_id'), nullable=False)
    previousStatus = db.Column(db.Integer, nullable=False)

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


class PreviousVerse(db.Model):
    __tablename__ = 'previousVerses'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_previousVerses'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    verse_id = db.Column(db.Integer, db.ForeignKey('verses.id', name='fk_previousVerses_verses_id'), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id', name='fk_previousVerses_actions_id'), nullable=False)
    previousVerse = db.Column(db.String(1000), nullable=False)


class Keyword(db.Model):
    __tablename__ = 'keywords'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_keywords'),)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id', name='fk_keywords_poem_id'), nullable=False)
    status = db.Column(db.Integer, nullable=True)
    keyword = db.Column(db.String(100), nullable=False)

class PreviousKeyword(db.Model):
    __tablename__ = 'previousKeywords'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_previousKeywords'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id', name='fk_previousKeywords_keywords_id'), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id', name='fk_previousKeywords_actions_id'), nullable=False)
    previousKeyword = db.Column(db.String(100), nullable=False)

class KeywordSuggestionBatch(db.Model):
    __tablename__ = 'keywordSuggestionBatches'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_keywordSuggestionBatches'),)
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id', name='fk_keywordSuggestionBatches_keywords_id'), nullable=False)
    batchNo = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now()
    )

class KeywordSuggestionCollection(db.Model):
    __tablename__ = 'keywordSuggestionCollections'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_keywordCollections'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keywordSuggestionBatch_id = db.Column(db.Integer, db.ForeignKey('keywordSuggestionBatches.id', name='fk_keywordCollections_keywordSuggestionBatches_id'), nullable=False)
    theme_id = db.Column(db.Integer, db.ForeignKey('themes.id', name='fk_keywordCollections_themes_id'), nullable=False)

class KeywordSuggestion(db.Model):
    __tablename__ = 'keywordSuggestions'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_keywordSuggestions'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id', name='fk_keywordSuggestions_keywords_id'), nullable=False)
    keywordSuggestionCollection_id = db.Column(db.Integer, db.ForeignKey('keywordSuggestionCollections.id', name='fk_keywordSuggestions_keywordSuggestionCollections_id'), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    suggestion = db.Column(db.String(100))

class SuggestionBatch(db.Model):
    __tablename__ = 'suggestionBatches'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_suggestionBatches'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    verse_id = db.Column(db.Integer, db.ForeignKey('verses.id', name='fk_suggestionBatches_verse_id'), nullable=False)
    batchNo = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now()
    )


class Suggestion(db.Model):
    __tablename__ = 'suggestions'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_suggestions'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    suggestionBatch_id = db.Column(db.Integer,
                                   db.ForeignKey('suggestionBatches.id', name='fk_suggestions_suggestionBatches_id'),
                                   nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)
    suggestion = db.Column(db.String(1000), nullable=False)


class RougeMetric(db.Model):
    __tablename__ = 'rougeMetrics'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_rougeMetrics'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rouge_metric = db.Column(db.String(10), nullable=False)

class RougeScore(db.Model):
    __tablename__ = 'rougeScores'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_rougeScores'),
                    db.UniqueConstraint('poem_id', 'verse_id', 'rougeMetric_id',
                                    name='uq_rougeScores_poem_verse_metric'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id', name='fk_rougeScores_poems_id'))
    verse_id = db.Column(db.Integer, db.ForeignKey('verses.id', name='fk_rougeScores_verses_id'))
    rougeMetric_id = db.Column(db.Integer, db.ForeignKey('rougeMetrics.id',
                                                         name='fk_rougeScores_rougeMetrics_id'),
                               nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1 = db.Column(db.Float, nullable=False)
    rougeMetric = db.relationship("RougeMetric")


class DistanceMetric(db.Model):
    __tablename__ = 'distanceMetrics'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_distanceMetrics'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    distance_metric = db.Column(db.String(50), nullable=False)

class DistanceScore(db.Model):
    __tablename__ = 'distanceScores'
    __table_args__ = (db.PrimaryKeyConstraint('id', name='pk_distanceScores'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id', name='fk_distanceScores_poems_id'))
    verse_id = db.Column(db.Integer, db.ForeignKey('verses.id', name='fk_distanceScores_verses_id'))
    distanceMetric_id = db.Column(db.Integer,
                                    db.ForeignKey('distanceMetrics.id',
                                                name='fk_distanceScores_distanceMetrics_id'),
                                    nullable=False)
    distance = db.Column(db.Float)
    similarity = db.Column(db.Float)
    distanceMetric = db.relationship("DistanceMetric")

