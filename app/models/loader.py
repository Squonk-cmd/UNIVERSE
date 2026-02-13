from app.models.rule_models import SimpleClassifier, EssayScorer
from app.models.ielts_evaluator import IELTSEvaluator # New import

MODELS = {
    "simple_classifier": SimpleClassifier(),
    "essay_scorer": EssayScorer(),
    "ielts_evaluator": IELTSEvaluator() # Added
}

def load_model(name):
    return MODELS[name]