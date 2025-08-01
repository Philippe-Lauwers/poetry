from .extensions import db
from rouge_metric import PyRouge
import jellyfish
from .dbModel import (
    Poem   as PoemModel,
    PreviousPoem    as PreviousPoemModel,
    Stanza  as StanzaModel,
    Verse   as VerseModel,
    PreviousVerse   as PreviousVerseModel,
    Action  as ActionModel,
    ActionType      as ActionTypeModel,
    ActionTarget    as ActionTargetModel,
    ActionTargetType as ActionTargetTypeModel,
    RougeMetric as RougeMetricModel,
    RougeScore as RougeScoreModel,
    DistanceMetric as DistanceMetricModel,
    DistanceScore as DistanceScoreModel
)


class BaseRouge:
    def __init__(self):
        pass

    def getScores(self, userInput: str, GRUInput: str):
        rouge = PyRouge(rouge_n=(1),
                        rouge_l=True,
                        rouge_w=True,
                        rouge_w_weight=1.2)
        rougeScores = rouge.evaluate([userInput], [GRUInput])
        for rougeMetric in rougeScores.keys():
            rougeMetricId = db.session.query(RougeMetricModel).filter(RougeMetricModel.rouge_metric == rougeMetric).first()
            rougeScores[rougeMetric]['rougeMetric_id'] = rougeMetricId.id

        damerau = jellyfish.damerau_levenshtein_distance(userInput, GRUInput)
        jaro_winkler = jellyfish.jaro_winkler_similarity(userInput, GRUInput)
        maxlen = max(len(userInput), len(GRUInput)) or 1
        distanceScores = {
            'damerau_levenshtein': {'distance': damerau,
                        'similarity': 1 - (damerau / maxlen)},
            'jaro_winkler': {'similarity': jaro_winkler}
        }
        for distanceMetric in distanceScores.keys():
            distanceMetricId = db.session.query(DistanceMetricModel).filter(
                DistanceMetricModel.distance_metric == distanceMetric).first()
            distanceScores[distanceMetric]['distanceMetric_id'] = distanceMetricId.id

        return {'rouge':rougeScores,'distance':distanceScores}

    def save(self, poem_id = None, verse_id = None, scoreDict = None):
        for scoreType, scores in scoreDict.items():
            if scoreType =='rouge':
                for rougeType in scores.keys():
                    RougeScore = RougeScoreModel(poem_id=poem_id, verse_id=verse_id, rougeMetric_id=scores[rougeType]['rougeMetric_id'], precision=scores[rougeType]['p'], recall=scores[rougeType]['r'], f1=scores[rougeType]['f'] )
                    db.session.merge(RougeScore)
                    db.session.flush()
            elif scoreType == 'distance':
                for distanceType in scores.keys():
                    if 'distance' in scores[distanceType].keys():
                        DistanceScore = DistanceScoreModel(poem_id=poem_id, verse_id=verse_id, distanceMetric_id=scores[distanceType]['distanceMetric_id'], distance=scores[distanceType]['distance'], similarity=scores[distanceType]['similarity'])
                    else:
                        DistanceScore = DistanceScoreModel(poem_id=poem_id, verse_id=verse_id, distanceMetric_id=scores[distanceType]['distanceMetric_id'], similarity=scores[distanceType]['similarity'])
                    db.session.merge(DistanceScore)
                    db.session.flush()


class PoemRougeScorer(BaseRouge):
    def __init__(self, poem: PoemModel):
        super().__init__()
        self.poem = poem

    def analyze(self):
        oldest = self.oldestAction()
        # Get scores for the poem if the user started from a generated draft
        if oldest == 'PM_GEN':
            user_input = self.poemUserInput()
            original   = self.original()
            self.save(poem_id=self.poem.id, scoreDict=self.getScores(user_input, original))
            pass
        # Get scores for verses in any case
        results = []
        for stanza in self.poem.stanzas:
            for verse in stanza.verses:
                vr = VerseRougeScorer(verse)
                results.append(vr.analyze())
                self.save(verse_id=verse.id, scoreDict=self.getScores(user_input, original))

        db.session.commit()

    def oldestAction(self) -> str:
        orm_oldest_action = (
            db.session
            .query(ActionTypeModel)
            .join(ActionModel, ActionModel.actionType_id == ActionTypeModel.id)
            .join(ActionTargetModel, ActionTargetModel.action_id == ActionModel.id)
            .join(ActionTargetTypeModel,
                  ActionTargetTypeModel.id == ActionTargetModel.actionTargetType_id)
            .filter(
                ActionTargetModel.target_id == self.poem.id,
                ActionTargetTypeModel.actionTargetType == 'poem',
            )
            .order_by(ActionModel.id.asc())
            .first()
        )
        return orm_oldest_action.actionType if orm_oldest_action else None

    def poemUserInput(self) -> str:
        return " ".join(
            v.text
            for stanza in self.poem.stanzas
            for v in stanza.verses
        )

    def original(self) -> str:
        # Grab the oldest PreviousPoem entry, if any
        verses = (
            db.session
            .query(VerseModel)
            .join(StanzaModel, VerseModel.stanza_id == StanzaModel.id)
            .filter(StanzaModel.poem_id == self.poem.id)
            .order_by(VerseModel.id)
            .all()
        )
        thePoem = []
        for v in verses:
            thePoem.append(VerseRougeScorer(v).original())
        return ' '.join(thePoem)


class VerseRougeScorer(BaseRouge):
    def __init__(self, verse: VerseModel):
        super().__init__()
        self.verse = verse

    def analyze(self):
        oldest = self.oldestAction()
        if oldest in ('VRS_GEN', 'SG_SEL'):
            candidate = self.verse.text
            reference = self.original()
            return self.getScores(candidate, reference)
        return None

    def oldestAction(self) -> str:
        orm_oldest = (
            db.session
            .query(ActionTypeModel)
            .join(ActionModel,        ActionModel.actionType_id     == ActionTypeModel.id)
            .join(ActionTargetModel,  ActionTargetModel.action_id   == ActionModel.id)
            .join(ActionTargetTypeModel,
                  ActionTargetTypeModel.id == ActionTargetModel.actionTargetType_id)
            .filter(
                ActionTargetModel.target_id == self.verse.id,
                ActionTargetTypeModel.actionTargetType == 'verse',
            )
            .order_by(ActionModel.id.asc())
            .first()
        )
        return orm_oldest.actionType if orm_oldest else None

    def original(self) -> str:
        prev = (
            db.session
            .query(PreviousVerseModel)
            .filter(PreviousVerseModel.verse_id == self.verse.id, PreviousVerseModel.previousVerse != "")
            .order_by(PreviousVerseModel.id.asc())
            .first()
        )
        return prev.previousVerse if prev else self.verse.verse
