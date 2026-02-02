from app.pipelines.classification import ClassificationPipeline
from app.pipelines.scoring import ScoringPipeline

PIPELINES = {
    "classification": ClassificationPipeline(),
    "scoring": ScoringPipeline()
}

def get_pipeline(name):
    return PIPELINES[name]
