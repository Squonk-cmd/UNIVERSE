from app.pipelines.base import BasePipeline
from app.models.loader import load_model
from app.preprocess.clean_text import clean_text
from app.postprocess.confidence import add_confidence

class ClassificationPipeline(BasePipeline):
    def run(self, input_data, config, options):
        text = clean_text(input_data)
        model = load_model(config["model"])
        result = model.predict(text)
        return add_confidence(result)
