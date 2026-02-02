from app.config_loader import load_task_config
from app.pipelines import get_pipeline

def route_task(sector, task, input_data, options):
    config = load_task_config(sector, task)
    pipeline = get_pipeline(config["pipeline"])
    return pipeline.run(input_data, config, options)
