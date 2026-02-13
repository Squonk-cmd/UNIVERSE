from app.pipelines.base import BasePipeline
from app.models.loader import load_model

class IELTSPipeline(BasePipeline):
    def run(self, input_data, config, options):
        model = load_model(config["model"])
        # The model handles both Task 1 (image+text) and Task 2 (text)
        result = model.evaluate(input_data)
        return result