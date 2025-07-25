# cli.py

from typing import Tuple, List, Set, Dict
import logging
from rich.logging import RichHandler

logger = logging.getLogger("mymaptool.cli")
logger.setLevel(logging.INFO)
handler = RichHandler(rich_tracebacks=True)
logger.addHandler(handler)

def choose_mode() -> bool:
    """
    Fragt den Nutzer, ob der normale oder der Spezialmodus gewählt werden soll.
    Rückgabe:
      False = normal
      True  = spezial
    """
    try:
        while True:
            ans = input("🛠️ Modus wählen – [n]ormal oder [s]pezial? ").strip().lower()
            if ans.startswith("n"):
                return False
            if ans.startswith("s"):
                return True
            print("❌ Ungültige Eingabe. Bitte mit 'n' oder 's' bestätigen.")
    except KeyboardInterrupt:
        logger.error("Eingabe abgebrochen.")
        raise

def choose_background_option() -> Dict[str, object]:
    """
    Spezialmodus: fragt, ob Hintergrund blau oder transparent sein soll.
    Gibt dict mit 'color' und 'transparent' zurück.
    """
    options = [
        ("Meeresblau   (#2896BA)", ("#2896BA", False)),
        ("Transparent (PNG-Hintergrund)", (None, True)),
    ]
    print("\nHintergrund wählen:")
    for i, (label, _) in enumerate(options, start=1):
        suffix = " (Standard)" if i == 1 else ""
        print(f"  [{i}] {label}{suffix}")

    while True:
        choice = input("Auswahl [1–2]: ").strip()
        if choice in {"1", "2"}:
            color, transp = options[int(choice) - 1][1]
            return {"color": color if color else "none", "transparent": transp}
        print("Ungültige Eingabe, bitte 1 oder 2 wählen.")


def choose_dimensions(is_special: bool, config: Dict) -> Tuple[int, int]:
    """
    Gibt die Kartengröße (width_px, height_px) zurück.
    - Im Normalmodus kommen die Werte aus config['karte'].
    - Im Spezialmodus fragt der User Breite und Höhe in Pixel ab.
    """
    if not is_special:
        w = config["karte"]["breite"]
        h = config["karte"]["hoehe"]
        logger.info(f"Normalmodus: Verwende {w}×{h} px aus config.json.")
        return w, h

    print("\nSpezialmodus aktiv: Bitte gewünschte Kartengröße eingeben (in Pixel).")
    while True:
        try:
            w = int(input("Breite  (px): ").strip())
            h = int(input("Höhe    (px): ").strip())
            if w <= 0 or h <= 0:
                print("❌ Werte müssen größer als 0 sein. Bitte erneut eingeben.")
                continue
            logger.info(f"Spezialmodus: Verwende benutzerdefinierte Größe {w}×{h} px.")
            return w, h
        except ValueError:
            print("❌ Ungültige Zahl. Bitte ganze Pixelwerte eingeben.")


def choose_region(config: Dict[str, List[str]]) -> Tuple[str, List[str]]:
    regions = list(config.get("regionen", {}))
    if not regions:
        logger.error("Keine Regionen in der Konfiguration gefunden.")
        raise ValueError("Keine Regionen in der Konfiguration gefunden.")

    print("\nVerfügbare Regionen:")
    for idx, name in enumerate(regions, 1):
        print(f"  {idx}. {name}")

    w = input("Bitte eine Region wählen (Nummer oder Name): ").strip()
    region_name = None
    if w.isdigit():
        idx = int(w) - 1
        if 0 <= idx < len(regions):
            region_name = regions[idx]
    elif w in regions:
        region_name = w

    if region_name is None:
        logger.error(f"Ungültige Region: {w}")
        raise ValueError(f"Ungültige Region: {w}")

    return region_name, config["regionen"][region_name]


def choose_scalebar_option() -> Dict[str, object]:
    options = [
        ("links unten", ("bottom-left", True)),
        ("rechts unten", ("bottom-right", True)),
        ("mitte unten", ("bottom-center", True)),
        ("keine Scalebar", (None, False)),
    ]

    print("\nScalebar erstellen?")
    for i, (label, _) in enumerate(options, start=1):
        suffix = " (Standard)" if i == 1 else ""
        print(f"  [{i}] {label}{suffix}")

    attempts = 0
    while True:
        choice = input("Auswahl [1–4]: ").strip()
        if choice in {"1", "2", "3", "4"}:
            pos, show = options[int(choice) - 1][1]
            return {"show": show, "position": pos or "bottom-left"}
        attempts += 1
        logger.warning(f"Ungültige Scalebar-Auswahl: {choice}")
        if attempts >= 3:
            logger.info("Standard-Scalebar wird verwendet.")
            return {"show": True, "position": "bottom-left"}
        print("Ungültige Eingabe, bitte 1–4 wählen.")


def choose_export_formats() -> Set[str]:
    """
    Spezialmodus: Auswahl der Exportformate.
    Standardmodus: gibt {'png'} zurück.
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

    if auswahl not in {"1", "2", "3"}:
        logger.info("Ungültige Auswahl, verwende Standard PNG.")
    return {"png"}
