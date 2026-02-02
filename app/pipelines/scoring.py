from app.pipelines.base import BasePipeline
from app.models.loader import load_model

class ScoringPipeline(BasePipeline):
    def run(self, input_data, config, options):
        model = load_model(config["model"])
        score = model.score(input_data)
        return {
            "score": score,
            "confidence": 0.8
        }
