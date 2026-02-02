from app.models.rule_models import SimpleClassifier, EssayScorer

MODELS = {
    "simple_classifier": SimpleClassifier(),
    "essay_scorer": EssayScorer()
}

def load_model(name):
    return MODELS[name]
