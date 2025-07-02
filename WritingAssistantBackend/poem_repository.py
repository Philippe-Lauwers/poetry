from .extensions import db
from .dbModel import Poem as PoemModel, Stanza as StanzaModel, Verse as VerseModel, Keyword as KeywordModel, \
    Action as ActionModel, ActionType as ActionTypeModel, ActionTarget as ActionTargetModel, \
    ActionTargetType as ActionTargetTypeModel

_actionType_id = {}
_actionTargetType_id = {}


class BaseRepository:
    @staticmethod
    def logAction(**logArgs):
        # Fetching arguments
        arg_actionType = logArgs['actionType']
        arg_actionTargetType = logArgs['actionTargetType']
        # Lookup, (create,) and cache of action-related ID's
        if not arg_actionType in _actionType_id:
            _actionType_id[arg_actionType] = db.session.query(ActionTypeModel).filter_by(
                actionType=arg_actionType.strip()).first().id
        if not arg_actionTargetType in _actionTargetType_id:
            _actionTargetType_id[arg_actionTargetType] = db.session.query(ActionTargetTypeModel).filter_by(
                actionTargetType=arg_actionTargetType.strip()).first().id
        id_actionType = _actionType_id[arg_actionType]
        id_actionTargetType = _actionTargetType_id[arg_actionTargetType]
        # Log the actions
        A = ActionModel(actionType_id=id_actionType)
        db.session.add(A)
        db.session.flush()
        # Attach target to action
        ActionTargetModel(action_id=A.id, actionTargetType_id=id_actionTargetType,
                          target_id=logArgs['targetID'])


class PoemRepository(BaseRepository):
    @staticmethod
    def save(poem, isNew=True):
        pass
        try:
            # create the poem record
            orm_poem = PoemModel(user_id=1,
                                 poemLanguage_id=poem.language,
                                 rhymeScheme_id=poem.form,
                                 theme_id=poem.nmfDim,
                                 status=1)
            db.session.add(orm_poem)
            db.session.flush()
            # store the poem id in the poem object because it will be used in the interface
            poem.id = orm_poem.id

            PoemRepository.logAction(actionType='PM_GEN', actionTargetType='poem', targetID=orm_poem.id)

            # save the stanzas
            for ST in poem.stanzas:
                StanzaRepository.save(ST, poem_id=orm_poem.id)
        except Exception as e:
            db.session.rollback()
            raise e

        db.session.commit()


class StanzaRepository(BaseRepository):
    @staticmethod
    def save(stanza, poem_id, isNew=True):
        # create the poem record
        orm_stanza = StanzaModel(poem_id=poem_id, order=stanza.order)
        db.session.add(orm_stanza)
        db.session.flush()
        # store the stanza id in the stanza object because it will be used in the interface
        stanza.id = orm_stanza.id

        StanzaRepository.logAction(actionType='ST_GEN', actionTargetType='stanza', targetID=orm_stanza.id)

        # save the stanzas
        for VS in stanza.verses:
            VerseRepository.save(VS, stanza_id=orm_stanza.id)


class VerseRepository(BaseRepository):
    @staticmethod
    def save(verse, stanza_id, isNew=True):
        # create the poem record
        orm_verse = VerseModel(stanza_id=stanza_id, order=verse.order,
                               status=1, verse=verse.text)
        db.session.add(orm_verse)
        db.session.flush()
        # store the verse id in the verse object because it will be used in the interface
        verse.id = orm_verse.id

        VerseRepository.logAction(actionType='VRS_GEN', actionTargetType='verse', targetID=orm_verse.id)


class KeywordRepository(BaseRepository):
    @staticmethod
    def save():
        print("keyword save not yet implemented")
