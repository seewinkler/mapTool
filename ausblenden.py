import geopandas as gpd

def select_ausblendbereiche(gpkg_path, verwendete_layer):
    """Interaktive Auswahl von Bereichen, die ausgeblendet werden sollen."""
    aktiv = False
    bereiche = {}

    antwort = input("🚫 Ausblenden aktivieren? [j/n]: ").strip().lower()
    if not antwort.startswith("j"):
        return {"aktiv": False, "bereiche": {}}

    aktiv = True

    if len(verwendete_layer) == 1:
        layer = verwendete_layer[0]
    else:
        print("\n📚 Layer, aus denen ausgeblendet werden kann:")
        for i, l in enumerate(verwendete_layer, 1):
            print(f"{i}. {l}")
        auswahl = input("🔍 Layer wählen (Nummer): ").strip()
        try:
            idx = int(auswahl) - 1
            layer = verwendete_layer[idx]
        except Exception:
            raise ValueError("Ungültige Layer-Auswahl für Ausblendung.")

    gdf = gpd.read_file(gpkg_path, layer=layer)
    region_names = sorted(gdf["NAME_1"].dropna().unique())

    print("\n🚫 Verfügbare Regionen zum Ausblenden:")
    for i, name in enumerate(region_names, 1):
        print(f"{i}. {name}")

    auswahl = input("Gib die Nummern der auszublendenden Regionen ein (z. B. 2,5,9): ")
    try:
        indices = [int(i.strip()) - 1 for i in auswahl.split(",")]
        namen = [region_names[i] for i in indices if 0 <= i < len(region_names)]
        bereiche[layer] = namen
    except Exception:
        print("⚠️ Ungültige Eingabe – keine Regionen ausgeblendet.")
        aktiv = False
        bereiche = {}

    return {"aktiv": aktiv, "bereiche": bereiche}