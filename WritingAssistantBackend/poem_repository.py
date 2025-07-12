from .extensions import db
from sqlalchemy import func
from .dbModel import Poem as PoemModel, Stanza as StanzaModel, Verse as VerseModel, Keyword as KeywordModel, \
    Action as ActionModel, ActionType as ActionTypeModel, ActionTarget as ActionTargetModel, \
    ActionTargetType as ActionTargetTypeModel, SuggestionBatch as SuggestionBatchModel, Suggestion as SuggestionModel

_actionType_id = {}
_actionTargetType_id = {}


class BaseRepository:
    @staticmethod
    def logAction(**logArgs):
        # Fetching arguments
        arg_actionType = logArgs['actionType']
        if 'actionTargetType' in logArgs.keys():
            arg_actionTargetType = logArgs['actionTargetType']
            arg_actionTargets = None
        if 'actionTargets' in logArgs.keys():
            arg_actionTargets = logArgs['actionTargets']
            arg_actionTargetType = None

        # Lookup, (create,) and cache of action-related ID's
        if not arg_actionType in _actionType_id:
            _actionType_id[arg_actionType] = db.session.query(ActionTypeModel).filter_by(
                actionType=arg_actionType.strip()).first().id
        if arg_actionTargetType is not None:
            if not arg_actionTargetType in _actionTargetType_id:
                _actionTargetType_id[arg_actionTargetType] = db.session.query(ActionTargetTypeModel).filter_by(
                    actionTargetType=arg_actionTargetType.strip()).first().id
        elif arg_actionTargets is not None:
            for target in arg_actionTargets.keys():
                if not target in _actionTargetType_id:
                    _actionTargetType_id[target] = db.session.query(ActionTargetTypeModel).filter_by(
                        actionTargetType=target.strip()).first().id

        id_actionType = _actionType_id[arg_actionType]

        # Log the actions
        A = ActionModel(actionType_id=id_actionType)
        db.session.add(A)
        db.session.flush()
        # Attach target to action
        if arg_actionTargetType is not None:
            id_actionTargetType = _actionTargetType_id[arg_actionTargetType]
            ATM = ActionTargetModel(action_id=A.id, actionTargetType_id=id_actionTargetType,
                              target_id=logArgs['targetID'])
            db.session.add(ATM)
        elif arg_actionTargets is not None:
            for target, targetID in arg_actionTargets.items():
                ATM = ActionTargetModel(action_id=A.id, actionTargetType_id=_actionTargetType_id[target],
                                  target_id=targetID)
                db.session.add(ATM)

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

        if verse.suggestions is not None and len(verse.suggestions) > 0:
            # save the suggestions
            SuggestionRepository.save(suggestions=verse.suggestions, verse_id=verse.id)

class SuggestionRepository(BaseRepository):
    @staticmethod
    def save(suggestions = None, verse_id = None):
        # First save a batch-stub for the suggestions
        orm_cntSuggestionBatches = (db.session.query(SuggestionBatchModel.verse_id.label("verse_id"),
                                                    func.count(SuggestionBatchModel.verse_id).label("count"))
                                                        .filter(SuggestionBatchModel.verse_id == verse_id)
                                                        .one_or_none())
        orm_suggestionBatch = SuggestionBatchModel(verse_id=verse_id, batchNo=orm_cntSuggestionBatches.count + 1)
        db.session.add(orm_suggestionBatch)
        db.session.flush()

        VerseRepository.logAction(actionType='SGB_GEN', actionTargetType='suggestion', targetID=orm_suggestionBatch.id)

        for s in suggestions:
            orm_suggestion = SuggestionModel(suggestionBatch_id=orm_suggestionBatch.id, suggestion=s.text)
            db.session.add(orm_suggestion)
            db.session.flush()
            s.id = orm_suggestion.id

    @staticmethod
    def acceptSuggestion(verse_id, suggestion_id):
        # This method is called when a user accepts a suggestion
        # - retrieve the suggestion
        try:
            orm_suggestion = db.session.query(SuggestionModel).filter_by(id=suggestion_id).first()
            if not orm_suggestion:
                raise ValueError("Suggestion not found")

            # - update the verse with the accepted suggestion
            orm_verse = db.session.query(VerseModel).filter_by(id=verse_id).first()
            if not orm_verse:
                raise ValueError("Verse not found")

            orm_verse.text = orm_suggestion.suggestion
            orm_suggestion.status = 1

            db.session.add(orm_verse)
            db.session.add(orm_suggestion)

            actionTargets = {'suggesion': suggestion_id, 'verse': verse_id}
            VerseRepository.logAction(actionType='SG_SEL', actionTargets = {'suggestion': suggestion_id, 'verse': verse_id})

        except Exception as e:
            print(f"Error accepting suggestion: {e}")
            db.session.rollback()
            raise e
        db.session.commit()
        return True


class KeywordRepository(BaseRepository):
    @staticmethod
    def save():
        print("keyword save not yet implemented")
