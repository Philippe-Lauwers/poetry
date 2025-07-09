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

    @staticmethod
    def isTmpId(id):
        # a tmp-id ends with "-tmp" and will generate an error when converted to int
        return isinstance(id, str) and id.endswith("-tmp")



class PoemRepository(BaseRepository):
    @staticmethod
    def save(poem):
        try:
            if poem.id is None:
            # new poem -> insert a new poem record
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

                if poem.origin == 'GRU':
                    actionType = 'PM_GEN'
                else: #if poem.origin == 'browser'
                    actionType = 'PM_WRT'
                PoemRepository.logAction(actionType=actionType, actionTargetType='poem', targetID=orm_poem.id)

            # save the stanzas, regardless of where the id came from (earlier interaction or created just nowp
            for ST in poem.stanzas:
                StanzaRepository.save(ST, poem_id=poem.id)
        except Exception as e:
            db.session.rollback()
            raise e

        db.session.commit()


class StanzaRepository(BaseRepository):
    @staticmethod
    def save(stanza, poem_id, isNew=True):
        doLog = True
        if stanza.id is None or str(stanza.id).endswith("-tmp"):
            # create the poem record
            orm_stanza = StanzaModel(poem_id=poem_id, order=stanza.order)
            db.session.add(orm_stanza)
            db.session.flush()

            if stanza.id is None:
                actionType = 'ST_GEN'
            else:
                actionType = 'ST_WRT'

            # store the stanza id in the stanza object because it will be used in the interface
            stanza.id = orm_stanza.id

        elif not str(stanza.id).isnumeric():
            # id from the browser, the part after the last '-' is the id from the database, the rest is prefix
            # here comes the update when the user has changed the poem
            stanza.id = stanza.id.split("-")[-1]
            actionType = ''
            doLog = False
        else:
            # id from the database, the stanza was not returned the browser,
            # no re-formatting or logging needed
            doLog = False

        if doLog: StanzaRepository.logAction(actionType=actionType, actionTargetType='stanza', targetID=stanza.id)

        # save the verses
        for VS in stanza.verses:
            VerseRepository.save(VS, stanza_id=stanza.id)


class VerseRepository(BaseRepository):
    @staticmethod
    def save(verse, stanza_id, isNew=True):
        doLog = True
        if verse.id is None or str(verse.id).endswith("-tmp"):
            # create the poem record
            orm_verse = VerseModel(stanza_id=stanza_id, order=verse.order,
                                   status=1, verse=verse.text)
            db.session.add(orm_verse)
            db.session.flush()

            if verse.id is None:
                actionType = 'VRS_GEN'
            else:
                actionType = 'VRS_WRT'

            # store the verse id in the verse object because it will be used in the interface
            verse.id = orm_verse.id

        elif not str(verse.id).isnumeric:
            # id from the browser, the part after the last '-' is the id from the database, the rest is prefix
            # here comes the update part
            verse.id = verse.id.split("-")[-1]
            actionType = 'VRS_WRT'
        else:
            # id from the database but the verse was not returned from the browser,
            # no re-formatting or logging needed
            doLog = False

        if doLog: VerseRepository.logAction(actionType=actionType, actionTargetType='verse', targetID=verse.id)


class KeywordRepository(BaseRepository):
    @staticmethod
    def save():
        print("keyword save not yet implemented")
