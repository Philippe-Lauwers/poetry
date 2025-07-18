from .extensions import db
from sqlalchemy import func
from .dbModel import Poem as PoemModel, PreviousPoem as PreviousPoemModel, PoemStatus as PoemStatusModel, \
    Stanza as StanzaModel, Verse as VerseModel, PreviousVerse as PreviousVerseModel, Keyword as KeywordModel, \
    Action as ActionModel, ActionType as ActionTypeModel, ActionTarget as ActionTargetModel, \
    ActionTargetType as ActionTargetTypeModel, SuggestionBatch as SuggestionBatchModel, Suggestion as SuggestionModel

_actionType_id = {}
_id_actionType = {}
_actionTargetType_id = {}
_id_actionTargetType = {}


class BaseRepository:
    @staticmethod
    def logAction(**logArgs):
        # Fetching arguments
        if not 'action' in logArgs.keys():
            arg_actionType = logArgs['actionType']
        elif 'action' in logArgs.keys():
            action_id = logArgs['action']
        if 'actionTargetType' in logArgs.keys():
            arg_actionTargetType = logArgs['actionTargetType']
            arg_actionTargets = None
        if 'actionTargets' in logArgs.keys():
            arg_actionTargets = logArgs['actionTargets']
            arg_actionTargetType = None

        # Lookup, (create,) and cache of action-related ID's
        if not 'action' in logArgs.keys():
            if not arg_actionType in _actionType_id:
                 _actionType_id[arg_actionType] = ActionRepository.actionType(arg_actionType)
        if arg_actionTargetType is not None:
            if not arg_actionTargetType in _actionTargetType_id:
               _actionTargetType_id[arg_actionTargetType] = ActionRepository.actionTarget(arg_actionTargetType)
        elif arg_actionTargets is not None:
            for target in arg_actionTargets.keys():
                if not target in _actionTargetType_id:
                    _actionTargetType_id[target] = ActionRepository.actionTarget(target)

        # Log the actions
        if not 'action' in logArgs.keys():
            id_actionType = _actionType_id[arg_actionType]
            A = ActionModel(actionType_id=id_actionType)
            db.session.add(A)
            db.session.flush()
            action_id = A.id
        # Attach target to action
        if arg_actionTargetType is not None:
            id_actionTargetType = _actionTargetType_id[arg_actionTargetType]
            ATt = ActionTargetModel(action_id=action_id, actionTargetType_id=id_actionTargetType,
                              target_id=logArgs['targetID'])
            db.session.add(ATt)
        elif arg_actionTargets is not None:
            for target, targetID in arg_actionTargets.items():
                ATt = ActionTargetModel(action_id=action_id, actionTargetType_id=_actionTargetType_id[target],
                                  target_id=targetID)
                db.session.add(ATt)

        db.session.flush()
        return action_id


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
                # look up the id of the status
                orm_status = db.session.query(PoemStatusModel).filter_by(poemStatusNo=poem.status).first()
                # create the poem record
                orm_poem = PoemModel(user_id=1,
                                     poemLanguage_id=poem.language,
                                     rhymeScheme_id=poem.form,
                                     theme_id=poem.nmfDim,
                                     status=orm_status.id)
                if poem.title is not None:
                    orm_poem.title = poem.title
                db.session.add(orm_poem)
                db.session.flush()
                # store the poem id in the poem object because it will be used in the interface
                poem.id = orm_poem.id

                if poem.origin == 'GRU':
                    actionType = 'PM_GEN'
                else: #if poem.origin == 'browser'
                    actionType = 'PM_WRT'
                PoemRepository.logAction(actionType=actionType, actionTargetType='poem', targetID=orm_poem.id)
            else:
                savePrevious = False
                actions = {}
                # lookup status id
                orm_status = db.session.query(PoemStatusModel).filter_by(poemStatusNo=poem.status).first()
                # change the poem record if needed
                orm_poem = db.session.query(PoemModel).filter_by(id=poem.id).first()
                if orm_poem.title != poem.title:
                    savePrevious = True
                    actions.update({'PM_UPD_TIT':0})
                if orm_poem.rhymeScheme_id != int(poem.form):
                    savePrevious = True
                    actions.update({'PM_UPD_FRM':0})
                if orm_poem.status != int(orm_status.id):
                    savePrevious = True
                    if int(poem.status) == 2:
                        actions.update({'PM_FIN':0})
                    elif int(poem.status) == 1:
                        actions.update({'PM_EDT':0})

                if savePrevious:
                    # log the action because we need the id for saving the previous version
                    AGroup = ActionModel(actionType_id=ActionRepository.actionType('PM_UPD'))
                    db.session.add(AGroup)
                    db.session.flush()
                    for action in actions.keys():
                        A = ActionModel(actionType_id=ActionRepository.actionType(actionType=action),group_id=AGroup.id)
                        db.session.add(A)
                        db.session.flush()
                        actions.update({action: A.id})
                    # save the previous version
                    orm_previousPoem = PreviousPoemModel(poem_id=orm_poem.id, action_id=AGroup.id,
                                                         previousTitle=orm_poem.title,
                                                         previousRhymeScheme_id=orm_poem.rhymeScheme_id,
                                                         previousStatus=orm_poem.status,
                                                         previousTheme_id=orm_poem.theme_id)
                    orm_poem.title = poem.title
                    orm_poem.rhymeScheme_id = poem.form
                    orm_poem.status = orm_status.id

                    db.session.add(orm_poem)
                    db.session.add(orm_previousPoem)
                    db.session.flush()

                    for action_id in actions.values():
                        VerseRepository.logAction(action=action_id,
                                                  actionTargets={'poem': poem.id, 'pr_poem': orm_previousPoem.id})

            # save the stanzas, regardless of where the id came from (earlier interaction or created just now
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
            # create the verse record
            orm_verse = VerseModel(stanza_id=stanza_id, order=verse.order,
                                   status=1, verse=verse.text)
            db.session.add(orm_verse)
            db.session.flush()

            if verse.suggestions is not None and len(verse.suggestions) > 0:
                actionType = 'VRS_SUG'
            elif verse.text == '': # an empty stub was created to attach suggestions to
                doLog = False
            else:
                actionType = 'VRS_WRT'

            # store the verse id in the verse object because it will be used in the interface
            verse.id = orm_verse.id

        elif str(verse.id).isnumeric:
            # The verse already exists in the database, we check whether the user has changed it

            orm_verse = db.session.query(VerseModel).filter_by(id=verse.id).first()
            if orm_verse.verse != verse.text:
                # Log the action first because we will need the id of the action
                actionType = 'VRS_UPD'
                actionType_id = ActionRepository.actionType(actionType=actionType)

                if orm_verse.verse=="":
                    print("verse accepted, yet action type is vrs_upd")

                A = ActionModel(actionType_id=actionType_id)
                db.session.add(A)
                db.session.flush()

                orm_previousVerse = PreviousVerseModel(action_id=A.id, verse_id=verse.id, previousVerse=orm_verse.verse)
                db.session.add(orm_previousVerse)
                db.session.flush()

                orm_verse = db.session.query(VerseModel).filter_by(id=verse.id).first()
                orm_verse.verse = verse.text
                db.session.add(orm_verse)

                VerseRepository.logAction(action=A.id,
                                          actionTargets={'verse': verse.id, 'pr_verse': orm_previousVerse.id})

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

            orm_verse.verse = orm_suggestion.suggestion
            orm_suggestion.status = 1

            db.session.add(orm_verse)
            db.session.add(orm_suggestion)

            VerseRepository.logAction(actionType='SG_SEL', actionTargets = {'suggestion': suggestion_id, 'verse': verse_id})

        except Exception as e:
            print(f"Error accepting suggestion: {e}")
            db.session.rollback()
            raise e
        db.session.commit()
        return True

    @staticmethod
    def lookupSuggestionsByVerse(verse_id):
        # This method returns all suggestions that were previously generated for a verse
        suggestions = []

        orm_suggestions = (db.session.query(SuggestionModel)
                          .join(SuggestionBatchModel, SuggestionModel.suggestionBatch_id == SuggestionBatchModel.id)
                          .filter(SuggestionBatchModel.verse_id == verse_id).all())
        if orm_suggestions:
           suggestions.extend([{"id":sugg.id,"suggestion":sugg.suggestion} for sugg in orm_suggestions])
           return suggestions
        else:
            return None


class KeywordRepository(BaseRepository):
    @staticmethod
    def save():
        print("keyword save not yet implemented")


class ActionRepository(BaseRepository):
    @staticmethod
    def actionType(actionType):
        # Looks up the actionType when an id is geiven and the id when an actionType is given
        if str(actionType).isnumeric():
            ATy = db.session.query(ActionTypeModel).filter_by(id=actionType.strip()).first()
            return ATy.actionType
        else:
            ATy = db.session.query(ActionTypeModel).filter_by(actionType=actionType.strip()).first()
            return ATy.id

    @staticmethod
    def actionTarget(actionTarget):
        # Looks up the actionTargetType when an id is geiven and the id when an actionTargetType is given
        if str(actionTarget).isnumeric():
            ATt = db.session.query(ActionTargetTypeModel).filter_by(id=actionTarget.strip()).first()
            return ATt.actionTargetType
        else:
            ATt = db.session.query(ActionTargetTypeModel).filter_by(actionTargetType=actionTarget.strip()).first()
            return ATt.id
