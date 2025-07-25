# config.py

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Union

# Standard-Pfade
BASE_DIR = Path(__file__).parent.resolve()
DEFAULT_CONFIG_PATH = BASE_DIR / "config.json"


def setup_logging(log_cfg: dict):
    """Initialisiert das Logging mit RotatingFileHandler."""
    level = log_cfg.get("level", "INFO").upper()
    log_file = log_cfg.get("file", "app.log")
    max_bytes = log_cfg.get("maxBytes", 5 * 1024 * 1024)
    backup_count = log_cfg.get("backupCount", 3)

    log_path = Path(log_file)
    if not log_path.is_absolute():
        log_path = BASE_DIR / log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        filename=str(log_path),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )

    root = logging.getLogger()
    root.setLevel(getattr(logging, level))
    root.addHandler(handler)

    suppress_modules = log_cfg.get("suppress_modules", [])
    for module_name in suppress_modules:
        logging.getLogger(module_name).setLevel(logging.WARNING)


def load_config(path: Union[str, Path] = None) -> dict:
    """
    Lädt die Konfiguration von disk,
    initialisiert Logging und gibt das Dict zurück.
    """
    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not cfg_path.is_absolute():
        cfg_path = BASE_DIR / cfg_path

    if not cfg_path.exists():
        raise FileNotFoundError(f"Konfigurationsdatei nicht gefunden: {cfg_path}")

    config = json.loads(cfg_path.read_text(encoding="utf-8"))

    # Logging-Bereich in config sicherstellen und initialisieren
    log_cfg = config.setdefault("logging", {})
    log_cfg["level"] = log_cfg.get("level", "INFO").upper()
    setup_logging(log_cfg)

    return config


# einmaliges Laden der config beim Import
CONFIG = load_config()

# Scalebar-Parameter global verfügbar machen
SCALER = CONFIG.get("scalebar", {})
