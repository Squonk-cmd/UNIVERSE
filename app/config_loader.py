import yaml
import os

def load_task_config(sector, task):
    path = f"sectors/{sector}.yaml"
    if not os.path.exists(path):
        raise ValueError("Sector not found")

    with open(path) as f:
        data = yaml.safe_load(f)

    if task not in data["tasks"]:
        raise ValueError("Task not found")

    return data["tasks"][task]
