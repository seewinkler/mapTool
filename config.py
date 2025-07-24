import json
from pathlib import Path

def load_config(path: str) -> dict:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    # hier Validierungs-Checks auf required keys etc.
    return config