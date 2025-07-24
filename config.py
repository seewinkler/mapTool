# config.py

import json
from pathlib import Path
from typing import Union

# Ermittelt das Verzeichnis, in dem config.py liegt
BASE_DIR = Path(__file__).parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.json"

def load_config(path: Union[str, Path] = None) -> dict:
    """
    Lädt die JSON-Konfiguration.
    Wenn kein Pfad übergeben wird, wird DEFAULT_CONFIG_PATH verwendet.
    """
    # Pfad auflösen
    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH

    # Relativen Pfad ins Modul-Verzeichnis mappen
    if not cfg_path.is_absolute():
        cfg_path = BASE_DIR / cfg_path

    if not cfg_path.exists():
        raise FileNotFoundError(f"Konfigurationsdatei nicht gefunden: {cfg_path}")

    # Einlesen & return
    return json.loads(cfg_path.read_text(encoding="utf-8"))