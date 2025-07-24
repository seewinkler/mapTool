# highlight_selector.py

import geopandas as gpd
import fiona

def select_highlight_regions(
    gpkg_path: str,
    config: dict,
    verbotene_namen: set[str] = None
) -> dict:
    """Interaktive Auswahl von Regionen zur Hervorhebung, mit Ausschlussliste."""
    highlight_cfg = config.get("hervorhebung", {})
    aktiv = False
    layer = highlight_cfg.get("layer", "")
    namen = []

    antwort = input("✨ Hervorhebung aktivieren? [j/n]: ").strip().lower()
    if not antwort.startswith("j"):
        return {"aktiv": False, "layer": "", "namen": []}

    aktiv = True

    # Layer-Auswahl
    available_layers = fiona.listlayers(gpkg_path)
    if layer not in available_layers:
        print("\n📚 Verfügbare Layer für Hervorhebung:")
        for i, l in enumerate(available_layers, 1):
            print(f"{i}. {l}")
        idx = int(input("🔍 Layer wählen (Nummer): ").strip()) - 1
        layer = available_layers[idx]

    # Regionen lesen
    # highlight_selector.py

    gdf = gpd.read_file(gpkg_path, layer=layer)
    region_names = sorted(gdf["NAME_1"].dropna().unique())

    # DEBUG: alle Namen vor Filter
    print("DEBUG – alle möglichen Regionen vor Filter:", region_names)

    if verbotene_namen:
        region_names = [n for n in region_names if n not in verbotene_namen]

    # DEBUG: nach Ausschluss der ausgeblendeten Namen
    print("DEBUG – nach Ausschluss ausgeblendeter Regionen:", region_names)
    # bereits ausgeblendete Namen entfernen
    if verbotene_namen:
        region_names = [n for n in region_names if n not in verbotene_namen]

    print("\n📍 Verfügbare Regionen zur Hervorhebung:")
    for i, name in enumerate(region_names, 1):
        print(f"{i}. {name}")

    auswahl = input("Gib die Nummern der Regionen ein (z. B. 3,7,15): ")
    indices = [int(i.strip()) - 1 for i in auswahl.split(",")]
    for i in indices:
        if 0 <= i < len(region_names):
            namen.append(region_names[i])

    if not namen:
        print("⚠️ Ungültige Eingabe – keine Regionen hervorgehoben.")
        aktiv = False

    return {"aktiv": aktiv, "layer": layer, "namen": namen}