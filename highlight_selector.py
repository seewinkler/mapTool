import geopandas as gpd
import fiona


def select_highlight_regions(gpkg_path, config, verbotene_namen=None):
    """Interaktive Auswahl von Regionen zur Hervorhebung."""
    highlight_config = config.get("hervorhebung", {})
    aktiv = False
    layer = highlight_config.get("layer", "")
    namen = []

    antwort = input("✨ Hervorhebung aktivieren? [j/n]: ").strip().lower()
    if not antwort.startswith("j"):
        return {"aktiv": False, "layer": "", "namen": []}

    aktiv = True

    # Layer-Auswahl (optional)
    available_layers = fiona.listlayers(gpkg_path)
    if layer not in available_layers:
        print("\n📚 Verfügbare Layer für Hervorhebung:")
        for i, l in enumerate(available_layers, 1):
            print(f"{i}. {l}")
        auswahl = input("🔍 Layer für Hervorhebung wählen (Nummer): ").strip()
        try:
            idx = int(auswahl) - 1
            layer = available_layers[idx]
        except Exception:
            raise ValueError("Ungültige Layer-Auswahl für Hervorhebung.")


    # Regionen anzeigen
    gdf = gpd.read_file(gpkg_path, layer=layer)
    region_names = sorted(gdf["NAME_1"].dropna().unique())

    # Ausgeblendete Namen entfernen
    if verbotene_namen:
        region_names = [name for name in region_names if name not in verbotene_namen]

    print("\n📍 Verfügbare Regionen zur Hervorhebung:")
    for i, name in enumerate(region_names, 1):
        print(f"{i}. {name}")

    auswahl = input("Gib die Nummern der Regionen ein (z. B. 3,7,15): ")
    try:
        indices = [int(i.strip()) - 1 for i in auswahl.split(",")]
        namen = [region_names[i] for i in indices if 0 <= i < len(region_names)]
    except Exception:
        print("⚠️ Ungültige Eingabe – keine Regionen hervorgehoben.")
        aktiv = False
        namen = []

    return {"aktiv": aktiv, "layer": layer, "namen": namen}
