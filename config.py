# config.py

import json
from pathlib import Path
from typing import Union

# Standard-Pfade
BASE_DIR = Path(__file__).parent.resolve()
DEFAULT_CONFIG_PATH = BASE_DIR / "config.json"


def load_config(path: Union[str, Path] = None) -> dict:
    """
    Lädt die JSON-Konfiguration. 
    Wenn kein Pfad übergeben wird, wird DEFAULT_CONFIG_PATH verwendet.
    Anschließend wird der logging.Block normalisiert:
      - Level wird uppercase
      - log.file wird relativ gesucht und bei Bedarf Verzeichnis angelegt
    """
    # 1) Pfad auflösen
    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not cfg_path.is_absolute():
        cfg_path = BASE_DIR / cfg_path

    if not cfg_path.exists():
        raise FileNotFoundError(f"Konfigurationsdatei nicht gefunden: {cfg_path}")

    # 2) Einlesen
    config = json.loads(cfg_path.read_text(encoding="utf-8"))

    # 3) Logging-Sektion validieren und anpassen
    log_cfg = config.get("logging", {})
    # Level auf Großbuchstaben normalisieren, Standard INFO
    level = log_cfg.get("level", "INFO").upper()
    config.setdefault("logging", {})["level"] = level

    # File-Pfad auflösen und Verzeichnis anlegen (falls angegeben)
    log_file = log_cfg.get("file")
    if log_file:
        log_path = Path(log_file)
        if not log_path.is_absolute():
            log_path = BASE_DIR / log_path

        # Sicherstellen, dass das Verzeichnis existiert
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Rückgabewert in String umwandeln
        config["logging"]["file"] = str(log_path)

    return config