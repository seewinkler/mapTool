# cli.py

from typing import Tuple, List
from rich.logging import RichHandler
import logging

logger = logging.getLogger("mymaptool.cli")

def choose_mode() -> bool:
    logger.debug("Modus-Auswahl gestartet")
    while True:
        ans = input("🛠️ Modus wählen – [n]ormal oder [s]pezial? ").strip().lower()
        if ans.startswith("n"):
            logger.info("Normalmodus gewählt")
            return False
        if ans.startswith("s"):
            logger.info("Spezialmodus gewählt")
            return True
        logger.warning("Ungültige Eingabe für Modus")

def choose_mode() -> bool:
    """
    Interaktive Auswahl des Modus.
    Gibt False für 'normal' und True für 'spezial' zurück.
    """
    while True:
        ans = input("🛠️ Modus wählen – [n]ormal oder [s]pezial? ").strip().lower()
        if ans.startswith("n"):
            return False
        if ans.startswith("s"):
            return True
        print("❌ Ungültige Eingabe. Bitte mit 'n' oder 's' bestätigen.")

def choose_region(config: dict) -> Tuple[str, List[str]]:
    """
    Interaktive Auswahl der Region.
    Liest aus config['regionen'] die verfügbaren Regionen aus,
    lässt den Nutzer per Nummer oder Name wählen
    und liefert (region_name, ziel_crs_list) zurück.
    """
    regions = list(config.get("regionen", {}))
    if not regions:
        raise ValueError("Keine Regionen in der Konfiguration gefunden.")

    print("\nVerfügbare Regionen:")
    for idx, name in enumerate(regions, 1):
        print(f"  {idx}. {name}")

    w = input("Bitte eine Region wählen (Nummer oder Name eingeben): ").strip()
    region_name = None

    if w.isdigit():
        idx = int(w) - 1
        if 0 <= idx < len(regions):
            region_name = regions[idx]
    else:
        if w in regions:
            region_name = w

    if region_name is None:
        raise ValueError(f"Ungültige Region: {w}")

    ziel_crs_list = config["regionen"][region_name]
    return region_name, ziel_crs_list

def choose_export_formats() -> set[str]:
    """
    Im Spezialmodus: Auswahl, ob PNG, SVG oder beides exportiert werden sollen.
    Standard: Nur PNG.
    """
    print("\n🎨 Exportformate wählen:")
    print("  [1] Nur PNG (Standard)")
    print("  [2] Nur SVG")
    print("  [3] PNG & SVG")

    auswahl = input("Format auswählen [1/2/3]: ").strip()
    if auswahl == "2":
        return {"svg"}
    if auswahl == "3":
        return {"png", "svg"}

    # Default
    return {"png"}
