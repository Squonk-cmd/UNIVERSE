from app.pipelines.classification import ClassificationPipeline
from app.pipelines.scoring import ScoringPipeline
from app.pipelines.ielts_pipeline import IELTSPipeline # New

PIPELINES = {
    "classification": ClassificationPipeline(),
    "scoring": ScoringPipeline(),
    "ielts_pipeline": IELTSPipeline() # Added
}

def get_pipeline(name):
    return PIPELINES[name]