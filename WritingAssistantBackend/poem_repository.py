from .extensions import db
from typing import Optional, overload, TYPE_CHECKING
from sqlalchemy import func, asc
from .dbModel import Poem as PoemModel, PreviousPoem as PreviousPoemModel, PoemStatus as PoemStatusModel, \
    Stanza as StanzaModel, Verse as VerseModel, PreviousVerse as PreviousVerseModel, Keyword as KeywordModel, \
    PreviousKeyword as PreviousKeywordModel, KeywordSuggestionBatch as KeywordSuggestionBatchModel, \
    KeywordSuggestionCollection as KeywordSuggestionCollectionModel, KeywordSuggestion as KeywordSuggestionModel, \
    Action as ActionModel, ActionType as ActionTypeModel, ActionTarget as ActionTargetModel, \
    ActionTargetType as ActionTargetTypeModel, SuggestionBatch as SuggestionBatchModel, Suggestion as SuggestionModel
from .poem_container import Poem

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


if TYPE_CHECKING:
    # Static type definitions only for mypy/pylance.
    class PoemRepository:
        @overload
        @staticmethod
        def fetch(*, key: str, id: None = ...) -> Poem: ...

        @overload
        @staticmethod
        def fetch(*, id: int, key: None = ...) -> Poem: ...


class PoemRepository(BaseRepository):
    @staticmethod
    def save(poem):
        KeywordSuggestionRepository.collectionId.clear()
        KeywordSuggestionBatchRepository.batchId = 0
        try:
            if poem.id is None or poem.id == '':
                # new poem -> insert a new poem record
                # look up the id of the status
                orm_status = db.session.query(PoemStatusModel).filter_by(poemStatusNo=poem.status).first()
                # create the poem record
                orm_poem = PoemModel(user_id=1,
                                     poemLanguage_id=poem.language,
                                     rhymeScheme_id=poem.form,
                                     theme_id=poem.nmfDim,
                                     status=orm_status.id,
                                     poemText=poem.text)
                if poem.title is not None:
                    orm_poem.title = poem.title
                db.session.add(orm_poem)
                db.session.flush()
                # store the poem id in the poem object because it will be used in the interface
                poem.id = orm_poem.id

                if poem.origin == 'GRU':
                    actionType = 'PM_GEN'
                elif poem.isStub():
                    actionType = 'PM_STB'
                else:  # if poem.origin == 'browser'
                    actionType = 'PM_WRT'
                PoemRepository.logAction(actionType=actionType, actionTargetType='poem', targetID=orm_poem.id)
            elif poem.isStub():
                orm_poemAction = (db.session.query(ActionModel)
                                    .join(
                                        ActionTargetModel,
                                        ActionTargetModel.action_id == ActionModel.id)
                                    .filter(  # 3
                                        ActionTargetModel.target_id == poem.id,
                                        ActionTargetModel.actionTargetType_id ==
                                        ActionRepository.actionTarget('poem'),
                                        ActionModel.actionType_id ==
                                        ActionRepository.actionType('PM_STB'))
                                    .first())

                orm_poem = db.session.query(PoemModel).filter_by(id=poem.id).first()
                orm_poem.title = poem.title
                orm_poem.rhymeScheme_id = poem.form
                orm_poem.poemText = poem.text

                # No logging required, we do not need to log the action, there is an action record, referring to
                # the poem, which was created when the stub was created, we only change the actionType_id to the
                # action corresponding to the poem origin
                if poem.origin is None:
                    pass
                elif poem.origin == 'GRU': # This is set at the start of generating a poem
                    orm_poemAction.actionType_id = ActionRepository.actionType('PM_GEN')
                elif poem.origin == 'browser': # This is set at the start of generating a verse (write with user input)
                    orm_poemAction.actionType_id = ActionRepository.actionType('PM_WRT')

            else:
                # if the poem is not a stub and we arrive here, it is the result of a save
                # in that case, if the type of the first action is 'PM_STB', we still have to
                # set the actionType_id of the first action to 'PM_WRT' because the poem was
                # (at least partially) written by the user, not generated
                orm_poemAction = (db.session.query(ActionModel)
                                  .join(
                    ActionTargetModel,
                    ActionTargetModel.action_id == ActionModel.id)
                                  .filter(  # 3
                    ActionTargetModel.target_id == poem.id,
                    ActionTargetModel.actionTargetType_id ==
                    ActionRepository.actionTarget('poem'),
                    ActionModel.actionType_id ==
                    ActionRepository.actionType('PM_STB'))
                                  .first())
                if poem.origin is None:
                    pass
                elif poem.origin == 'GRU':  # This is set at the start of generating a poem
                    orm_poemAction.actionType_id = ActionRepository.actionType('PM_GEN')
                elif poem.origin == 'browser':  # This is set at the start of generating a verse (write with user input)
                    orm_poemAction.actionType_id = ActionRepository.actionType('PM_WRT')

                savePrevious = False
                actions = {}
                # lookup status id
                orm_status = db.session.query(PoemStatusModel).filter_by(poemStatusNo=poem.status).first()
                # change the poem record if needed
                orm_poem = db.session.query(PoemModel).filter_by(id=poem.id).first()
                if orm_poem.title != poem.title:
                    savePrevious = True
                    actions.update({'PM_UPD_TIT': 0})
                if orm_poem.rhymeScheme_id != int(poem.form):
                    savePrevious = True
                    actions.update({'PM_UPD_FRM': 0})
                if orm_poem.status != int(orm_status.id):
                    savePrevious = True
                    if int(poem.status) == 2:
                        actions.update({'PM_FIN': 0})
                    elif int(poem.status) == 1:
                        actions.update({'PM_EDT': 0})
                if orm_poem.poemText =="" or orm_poem.poemText != poem.text:
                    orm_poem.poemText = poem.text

                if savePrevious:
                    # log the action because we need the id for saving the previous version
                    AGroup = ActionModel(actionType_id=ActionRepository.actionType('PM_UPD'))
                    db.session.add(AGroup)
                    db.session.flush()
                    for action in actions.keys():
                        A = ActionModel(actionType_id=ActionRepository.actionType(actionType=action),
                                        group_id=AGroup.id)
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
            for KW in poem.keywords:
                KeywordRepository.save(KW, poem_id=poem.id)
        except Exception as e:
            db.session.rollback()
            raise e

        db.session.commit()

    @staticmethod
    def list(user_id, status=None):
        poems = []

        # Base query, joining Poem → PoemStatus on the status FK
        query = (
            db.session
            .query(
                PoemModel.id,
                PoemModel.lookupKey,
                PoemModel.title,
                PoemModel.poemLanguage_id,
                PoemModel.rhymeScheme_id,
                PoemModel.poemText,
                PoemStatusModel.poemStatusNo.label("poemStatusNo"))
            .join(PoemStatusModel, PoemStatusModel.id == PoemModel.status)
            .filter(PoemModel.user_id == user_id)
        )

        # Add status filter
        if status is None:
            query = query.filter(PoemStatusModel.poemStatusNo > 0)
        else:
            query = query.filter(PoemStatusModel.poemStatusNo == status)

        # Order and execute
        orm_list = query.order_by(asc(PoemModel.id)).all()

        # Build result list
        for pm in orm_list:
            poem_dict = {
                "id": pm.id,
                "key": pm.lookupKey,
                "title": pm.title,
                "language": pm.poemLanguage_id,
                "form": pm.rhymeScheme_id,
                "status": pm.poemStatusNo,
                "text": pm.poemText,
            }

            # If it’s a “stub,” fetch keywords to display
            if not pm.title and not pm.poemText:
                orm_keywords = (
                    db.session
                    .query(KeywordModel)
                    .filter(
                        KeywordModel.poem_id == pm.id,
                        KeywordModel.status > 0
                    )
                    .order_by(asc(KeywordModel.id))
                    .all()
                )
                poem_dict["keywords"] = [{kw.id: kw.keyword} for kw in orm_keywords]
                poem_dict["keywordsText"] = ", ".join([kw.keyword for kw in orm_keywords])

            poems.append(poem_dict)

        return poems

    @staticmethod
    def delete(key):
        # Delete a poem by its key
        orm_poem = db.session.query(PoemModel).filter_by(lookupKey=key).first()
        if not orm_poem:
            return {"error": "Poem not found"}, 404

        # Set status to 0 (deleted)
        orm_poem.status = 0
        db.session.commit()

        BaseRepository.logAction(actionType='PM_DEL', actionTargetType='poem', targetID=orm_poem.id)

        return key

    @staticmethod
    @overload
    def fetch(*, key: str, id: None = ...) -> Poem:
        ...

    @staticmethod
    @overload
    def fetch(*, id: int, key: None = ...) -> Poem:
        ...

    @staticmethod
    def fetch(*, key: Optional[str] = None, id: Optional[int] = None):

        from .poem_container import Poem
        # Fetch a poem from the database by its key
        orm_poem = (db.session
                    .query(PoemModel.id.label("id"),
                           PoemModel.rhymeScheme_id.label("form"),
                           PoemModel.poemLanguage_id.label("lang"),
                           PoemModel.theme_id.label("nmfDim"),
                           PoemModel.status,
                           PoemModel.title,
                           StanzaModel.id.label("stanza_id"))
                    .outerjoin(StanzaModel, StanzaModel.poem_id == PoemModel.id))

        if key is not None:
            orm_poem = orm_poem.filter(PoemModel.lookupKey == key)
        elif id is not None:
            orm_poem = orm_poem.filter(PoemModel.id == id)
        orm_poem = orm_poem.all()

        if not orm_poem:
            return {"error": "Poem not found"}, 404

        orm_status = db.session.query(PoemStatusModel).filter_by(id=orm_poem[0].status).first()

        # Create a Poem container object
        poemContainer = Poem(id=orm_poem[0].id, title=orm_poem[0].title, form=orm_poem[0].form, lang=orm_poem[0].lang,
                             status=orm_status.poemStatusNo, nmfDim=orm_poem[0].nmfDim)

        # Add stanzas to the poem object
        for stanza in orm_poem:
            stanza_id = stanza.stanza_id
            stanzaContainer = StanzaRepository.fetch(stanza_id=stanza_id)
            poemContainer.addStanza(stanza=stanzaContainer)

        # Add keywords to the poem object (if any)
        orm_keywords = (db.session.query(KeywordModel.id, KeywordModel.keyword).
                        filter(KeywordModel.poem_id == poemContainer.id).
                        filter(KeywordModel.status > 1).all())
        for kw in orm_keywords:
            poemContainer.addKeyword(id=kw.id, keyword=kw.keyword)

        # Return the poem object
        return poemContainer


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

    @staticmethod
    def fetch(stanza_id):
        from .poem_container import Stanza
        orm_stanza = (db.session.query(StanzaModel.id, StanzaModel.order, VerseModel.id.label("verse_id"), )
                      .join(VerseModel, StanzaModel.id == VerseModel.stanza_id)
                      .filter(StanzaModel.id == stanza_id).all())
        if not orm_stanza:
            return {"error": "Stanza not found"}, 404

        # Create a Stanza container object
        stanza = Stanza(id=orm_stanza[0].id)
        stanza.order = orm_stanza[0].order
        # Append verses to the stanza object
        for verse in orm_stanza:
            verse_id = verse.verse_id
            verseContainer = VerseRepository.fetch(verse_id=verse_id)
            stanza.addVerse(verse=verseContainer)

        return stanza


class VerseRepository(BaseRepository):
    @staticmethod
    def save(verse, stanza_id, isNew=True):
        doLog = True
        if verse.id is None or str(verse.id).endswith("-tmp"):
            # create the verse record
            orm_verse = VerseModel(stanza_id=stanza_id, order=verse.order,
                                   status=2, verse=verse.text)
            db.session.add(orm_verse)
            db.session.flush()

            if verse.suggestions is not None and len(verse.suggestions) > 0:
                actionType = 'VRS_SUG'
            elif verse.text == '':  # an empty stub was created to attach suggestions to
                doLog = False
            else:
                actionType = 'VRS_WRT'

            # store the verse id in the verse object because it will be used in the interface
            verse.id = orm_verse.id

        elif str(verse.id).isnumeric:
            # The verse already exists in the database, we check whether the user has changed it

            orm_verse = db.session.query(VerseModel).filter_by(id=verse.id).first()
            if orm_verse.verse != verse.text and orm_verse.verse != "":
                # Log the action first because we will need the id of the action
                if verse.origin == 'GRU':
                    actionType = 'VRS_GEN'
                else:
                    actionType = 'VRS_UPD'
                actionType_id = ActionRepository.actionType(actionType=actionType)

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
                if orm_verse.verse == "":
                    # The verse record was created as a stub to attach suggestions to it
                    # The new text was generated automatically in the context of an entire poem
                    # Acceptation of a suggestion is handled in SuggestionRepository
                    orm_verse.verse = verse.text
                    db.session.add(orm_verse)
                # id from the database but the verse was not returned from the browser,
                # no re-formatting or logging needed
                doLog = False

        if doLog: VerseRepository.logAction(actionType=actionType, actionTargetType='verse', targetID=verse.id)

        if verse.suggestions is not None and len(verse.suggestions) > 0:
            # save the suggestions
            SuggestionRepository.save(suggestions=verse.suggestions, verse_id=verse.id)

    @staticmethod
    def fetch(verse_id):
        from .poem_container import Verse
        orm_verse = (db.session.query(VerseModel.id, VerseModel.verse)
                     .filter(VerseModel.id == verse_id).first())
        if not orm_verse:
            return {"error": "Verse not found"}, 404
        # Create and return a Verse container object
        verse = Verse(id=orm_verse.id, verseText=orm_verse.verse)
        return verse


class SuggestionRepository(BaseRepository):
    @staticmethod
    def save(suggestions=None, verse_id=None):
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
            orm_suggestion.status = 3  # final/accepted

            db.session.add(orm_verse)
            db.session.add(orm_suggestion)

            orm_poem = (db.session.query(PoemModel).join(StanzaModel, PoemModel.id == StanzaModel.poem_id)
                        .join(VerseModel, StanzaModel.id == VerseModel.stanza_id)
                        .filter(VerseModel.id == verse_id).first())
            nmfDim = orm_poem.theme_id

            VerseRepository.logAction(actionType='SG_SEL',
                                      actionTargets={'suggestion': suggestion_id, 'verse': verse_id})

            output = {"verse_id": verse_id, "verse_text": orm_suggestion.suggestion, "nmfDim": nmfDim}
        except Exception as e:
            print(f"Error accepting suggestion: {e}")
            db.session.rollback()
            raise e
        db.session.commit()
        return output

    @staticmethod
    def lookupSuggestionsByVerse(verse_id):
        # This method returns all suggestions that were previously generated for a verse
        suggestions = []

        orm_suggestions = (db.session.query(SuggestionModel)
                           .join(SuggestionBatchModel, SuggestionModel.suggestionBatch_id == SuggestionBatchModel.id)
                           .filter(SuggestionBatchModel.verse_id == verse_id).all())
        if orm_suggestions:
            suggestions.extend([{"id": sugg.id, "suggestion": sugg.suggestion} for sugg in orm_suggestions])
            return suggestions
        else:
            return None


class KeywordRepository(BaseRepository):
    @staticmethod
    def save(keyword, poem_id):
        if keyword.id is None or str(keyword.id).endswith("-tmp"):
            # create the keyword record
            orm_keyword = KeywordModel(poem_id=poem_id, keyword=keyword.text, status=2)  # status 2 = active/draft
            db.session.add(orm_keyword)
            db.session.flush()

            # store the keyword id in the keyword object because it will be used in the interface
            keyword.id = orm_keyword.id

            # the keyword is new and it has suggestions -> the it is generated, else it is provided by the user
            if keyword.suggestions is not None and len(keyword.suggestions) > 0:
                actionType = 'KW_GEN'
            else:
                actionType = 'KW_WRT'

            KeywordRepository.logAction(actionType=actionType, actionTargetType='keyword', targetID=keyword.id)
        elif str(keyword.id).isnumeric():
            # The keyword already exists in the database, we check whether the user has changed it
            orm_keyword = db.session.query(KeywordModel).filter_by(id=keyword.id).first()
            if orm_keyword.keyword != keyword.text and orm_keyword.keyword != "":
                # Log the action first because we will need the id of the action
                actionType = 'KW_UPD'
                A = ActionModel(actionType_id=ActionRepository.actionType(actionType=actionType))
                db.session.add(A)
                db.session.flush()

                orm_previousKeyword = PreviousKeywordModel(action_id=A.id, keyword_id=keyword.id,
                                                           previousKeyword=orm_keyword.keyword)
                db.session.add(orm_previousKeyword)
                db.session.flush()

                orm_keyword.keyword = keyword.text
                db.session.add(orm_keyword)
                db.session.flush()

                pass
                KeywordRepository.logAction(action=A.id,
                                            actionTargets={'keyword': orm_keyword.id,
                                                           'pr_keyword': orm_previousKeyword.id})
                pass
            else:
                # id from the database but the keyword was not returned from the browser,
                # no re-formatting or logging needed
                pass

        if keyword.suggestions is not None and len(keyword.suggestions) > 0:
            # save the suggestions
            KeywordSuggestionBatchRepository.save(keywordSuggestions=keyword.suggestions, keyword_id=keyword.id)

    @staticmethod
    def deleteKeyword(keyword_id):
        orm_keyword = db.session.query(KeywordModel).filter_by(id=keyword_id).first()
        orm_keyword.status = 0  # deleted

        BaseRepository.logAction(actionType='KW_DEL', actionTargetType='keyword', targetID=keyword_id)
        db.session.add(orm_keyword)
        db.session.commit()

        return {"deleted": keyword_id}

    @staticmethod
    def lookupKeywordsByPoem(poem_id):
        orm_keywords4poem = db.session.query(KeywordModel).filter(KeywordModel.poem_id == poem_id).order_by(
            asc(KeywordModel.id)).all()
        keywords = {}
        if orm_keywords4poem:
            for kw in orm_keywords4poem:
                keywords[kw.id] = {"id": kw.id, "text": kw.keyword, "suggestions": []}
        return keywords


class KeywordSuggestionBatchRepository(BaseRepository):
    batchId = 0

    @staticmethod
    def save(keywordSuggestions, keyword_id):
        # Here, the suggestions are grouped in a batch and the creation of the batch is logged
        if KeywordSuggestionBatchRepository.batchId == 0:
            orm_cntKeywordSuggestionBatches = (
                db.session.query(KeywordSuggestionBatchModel.keyword_id.label("keyword_id"),
                                 func.count(KeywordSuggestionBatchModel.keyword_id).label(
                                     "count"))
                .filter(KeywordSuggestionBatchModel.keyword_id == keyword_id)
                .one_or_none())
            orm_keywordSuggestionBatch = KeywordSuggestionBatchModel(keyword_id=keyword_id,
                                                                     batchNo=orm_cntKeywordSuggestionBatches.count + 1)
            db.session.add(orm_keywordSuggestionBatch)
            db.session.flush()
            KeywordSuggestionBatchRepository.batch_id = orm_keywordSuggestionBatch.id

            KeywordRepository.logAction(actionType='KWSB_GEN', actionTargetType='keyword_suggestion_batch',
                                        targetID=orm_keywordSuggestionBatch.id)

        KeywordSuggestionRepository.save(keywordSuggestions=keywordSuggestions, keyword_id=keyword_id,
                                         keywordBatch_id=KeywordSuggestionBatchRepository.batch_id)


class KeywordSuggestionRepository(BaseRepository):
    collectionId = {}

    @staticmethod
    def save(keywordSuggestions, keyword_id, keywordBatch_id):
        # Here, the suggestions are grouped in collections of n (the number of keywords to generate) keywords
        for suggColl in range(len(keywordSuggestions)):
            if not suggColl in KeywordSuggestionRepository.collectionId:
                orm_keywordSuggestionCollection = KeywordSuggestionCollectionModel(
                    keywordSuggestionBatch_id=keywordBatch_id, theme_id=keywordSuggestions[suggColl].nmfDim, )
                db.session.add(orm_keywordSuggestionCollection)
                db.session.flush()
                KeywordSuggestionRepository.collectionId[suggColl] = orm_keywordSuggestionCollection.id

            orm_keywordSuggestion = KeywordSuggestionModel(keyword_id=keyword_id,
                                                           keywordSuggestionCollection_id=
                                                           KeywordSuggestionRepository.collectionId[suggColl],
                                                           suggestion=keywordSuggestions[suggColl].suggestion,
                                                           status=2)
            db.session.add(orm_keywordSuggestion)
            db.session.flush()
            keywordSuggestions[suggColl].id = orm_keywordSuggestion.id
            keywordSuggestions[suggColl].collectionId = KeywordSuggestionRepository.collectionId[suggColl]

    @staticmethod
    def accepKWCollection(suggestionCollection_id):
        output = {}
        # 1) lookup the suggestions linked to this collection
        orm_suggestions4collectionId = db.session.query(KeywordSuggestionModel).filter_by(
            keywordSuggestionCollection_id=suggestionCollection_id).all()
        # 2) lookup the collection (theme_id) to which the suggestions belong
        orm_suggestionCollection = db.session.query(KeywordSuggestionCollectionModel).filter_by(
            id=suggestionCollection_id).first()
        # 3) log the action, targets will be logged hereafter
        actionType = 'KWS_SEL'
        A = ActionModel(actionType_id=ActionRepository.actionType(actionType=actionType))
        db.session.add(A)
        db.session.flush()
        # 4) update the status of the suggestions: set their value and set the status to 3 (accepted/final)
        for suggestion in orm_suggestions4collectionId:
            suggestion.status = 3
            orm_keyword = db.session.query(KeywordModel).filter_by(id=suggestion.keyword_id).first()
            orm_keyword.keyword = suggestion.suggestion
            db.session.add(orm_keyword)
            db.session.add(suggestion)
            db.session.flush()

            BaseRepository.logAction(action=A.id,
                                     actionTargets={'keyword': suggestion.keyword_id,
                                                    'keyword_suggestion': suggestion.id,
                                                    'keyword_suggestion_collection': suggestionCollection_id})

            output[suggestion.keyword_id] = suggestion.suggestion

        db.session.commit()
        return {'nmfDim': orm_suggestionCollection.theme_id, 'keywords': output}


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
