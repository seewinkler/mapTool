import os
import json
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 📁 Basisverzeichnisse
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
hauptland_path = os.path.join(BASE_DIR, "hauptland")
nebenland_path = os.path.join(BASE_DIR, "nebenlaender")
output_path = os.path.join(BASE_DIR, "output")
config_path = os.path.join(BASE_DIR, "config.json")

# 🧾 Konfiguration laden
with open(config_path, encoding="utf-8") as f:
    config = json.load(f)

# 📐 Kartengröße und Seitenverhältnis
breite_px = config["karte"]["breite"]
hoehe_px = config["karte"]["hoehe"]
seitenverhaeltnis = breite_px / hoehe_px
dpi = 100
figsize = (breite_px / dpi, hoehe_px / dpi)

# 🎨 Farben
farbe_hauptland = config["farben"]["hauptland"]
farbe_nebenland = config["farben"]["nebenland"]
farbe_grenze = config["farben"]["grenze"]
highlight_color = config["farben"]["highlight"]

# 🔍 Regionsauswahl
regionen = list(config["regionen"].keys())
print("Verfügbare Regionen:")
for i, r in enumerate(regionen, 1):
    print(f"{i}. {r}")

wahl = input("Bitte eine Region wählen (Nummer oder Name eingeben): ").strip()
region = None
if wahl.isdigit():
    idx = int(wahl) - 1
    if 0 <= idx < len(regionen):
        region = regionen[idx]
else:
    if wahl in regionen:
        region = wahl
if not region:
    raise ValueError("Ungültige Region.")

ziel_crs_liste = config["regionen"][region]

# 📂 Hauptland-Datei laden
hauptland_dateien = [f for f in os.listdir(hauptland_path) if f.endswith(".gpkg")]
if not hauptland_dateien:
    raise FileNotFoundError("Keine Hauptland-GPKG-Datei gefunden.")
hauptland_file = hauptland_dateien[0]
hauptland_gpkg = os.path.join(hauptland_path, hauptland_file)

# 📂 Nebenländer-Dateien laden
nebenland_dateien = [f for f in os.listdir(nebenland_path) if f.endswith(".gpkg")]
nebenlaender_gdfs = []
for datei in nebenland_dateien:
    pfad = os.path.join(nebenland_path, datei)
    gdf = gpd.read_file(pfad, layer=config["nebenlaender"])
    nebenlaender_gdfs.append(gdf)

# 🗺️ Hauptland-Layer laden und vereinigen
gdf_haupt_list = []
for layer in config["hauptland"]:
    gdf = gpd.read_file(hauptland_gpkg, layer=layer)

    if config["ausblenden"]["aktiv"]:
        ausblend_bereiche = config["ausblenden"]["bereiche"]
        if layer in ausblend_bereiche:
            namen = ausblend_bereiche[layer]
            gdf = gdf[~gdf["NAME_1"].isin(namen)]  # ggf. Spaltenname prüfen
            print(f"Aus Layer '{layer}' ausgeblendet: {namen}")

    gdf_haupt_list.append(gdf)

gdf_haupt = pd.concat(gdf_haupt_list, ignore_index=True)

# 🔦 Hervorhebung vorbereiten (nur Namen merken)
highlight_config = config["hervorhebung"]
highlight_layer = highlight_config["layer"]
gewaehlte_namen = []
if highlight_config["aktiv"]:
    print("\n📍 Verfügbare Regionen für Hervorhebung:")
    gdf_highlight_source = gpd.read_file(hauptland_gpkg, layer=highlight_layer)
    region_names = sorted(gdf_highlight_source["NAME_1"].dropna().unique())

    for i, name in enumerate(region_names, 1):
        print(f"{i}. {name}")

    auswahl = input("\nGib die Nummern der Regionen ein, durch Komma getrennt (z. B. 3,7,15): ")
    try:
        indices = [int(i.strip()) - 1 for i in auswahl.split(",")]
        gewaehlte_namen = [region_names[i] for i in indices if 0 <= i < len(region_names)]
        print(f"Hervorgehobene Regionen: {gewaehlte_namen}")
    except Exception:
        print("Ungültige Eingabe – keine Hervorhebung aktiv.")
        gewaehlte_namen = []

# 🔁 Karten für alle Projektionen
for ziel_crs in ziel_crs_liste:
    ziel_crs_safe = ziel_crs.replace(":", "_")

    gdf_haupt_proj = gdf_haupt.to_crs(ziel_crs)
    nebenlaender_proj = [gdf.to_crs(ziel_crs) for gdf in nebenlaender_gdfs]

    # ✨ Hervorhebung reprojizieren
    if highlight_config["aktiv"] and gewaehlte_namen:
        gdf_highlight_source_proj = gdf_highlight_source.to_crs(ziel_crs)
        gdf_highlight = gdf_highlight_source_proj[
            gdf_highlight_source_proj["NAME_1"].isin(gewaehlte_namen)
        ]
    else:
        gdf_highlight = None

    # 🔲 Bounding Box
    minx, miny, maxx, maxy = gdf_haupt_proj.total_bounds
    width = maxx - minx
    height = maxy - miny
    center_x = (minx + maxx) / 2
    center_y = (miny + maxy) / 2

    current_ratio = width / height
    if current_ratio > seitenverhaeltnis:
        new_height = width / seitenverhaeltnis
        new_width = width
    else:
        new_width = height * seitenverhaeltnis
        new_height = height

    new_width *= 1.05
    new_height *= 1.05
    bbox = (
        center_x - new_width / 2,
        center_x + new_width / 2,
        center_y - new_height / 2,
        center_y + new_height / 2
    )

    # 🖼️ Plot
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    for gdf in nebenlaender_proj:
        gdf.plot(ax=ax, color=farbe_nebenland, edgecolor=farbe_grenze)
    gdf_haupt_proj.plot(ax=ax, color=farbe_hauptland, edgecolor=farbe_grenze)
    if gdf_highlight is not None and not gdf_highlight.empty:
        gdf_highlight.plot(ax=ax, color=highlight_color, edgecolor=farbe_grenze)

    ax.set_xlim(bbox[0], bbox[1])
    ax.set_ylim(bbox[2], bbox[3])
    ax.axis("off")

    # 💾 Speichern
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename_png = f"{os.path.splitext(hauptland_file)[0]}_{region}_{ziel_crs_safe}_{timestamp}.png"
    output_filepath_png = os.path.join(output_path, output_filename_png)
    plt.savefig(output_filepath_png, dpi=dpi, bbox_inches=None, pad_inches=0, transparent=True)

    # 💾 Speichern als SVG
    output_filename_svg = f"{os.path.splitext(hauptland_file)[0]}_{region}_{ziel_crs_safe}_{timestamp}.svg"
    output_filepath_svg = os.path.join(output_path, output_filename_svg)
    plt.savefig(output_filepath_svg, format="svg", bbox_inches=None, pad_inches=0)

    # 🧹 Plot schließen
    plt.close()

    print(f"Karten gespeichert unter:\n → PNG: {output_filepath_png}\n → SVG: {output_filepath_svg}")