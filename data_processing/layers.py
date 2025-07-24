# data_processing/layers.py

import pandas as pd
import geopandas as gpd

from layer_selector import get_layers_interactive
from ausblenden import select_ausblendbereiche
from highlight_selector import select_highlight_regions

def merge_hauptland_layers(
    gpkg_path: str, config: dict, spezialmodus: bool
) -> gpd.GeoDataFrame:
    """
    Liest alle im Config- oder Interaktiv-Modus ausgewählten
    Hauptland-Layer ein und vereinigt sie zu einem GeoDataFrame.
    """
    if spezialmodus:
        layers = get_layers_interactive(gpkg_path)
    else:
        layers = config.get("hauptland", [])

    gdfs = []
    for layer in layers:
        gdf = gpd.read_file(gpkg_path, layer=layer)
        gdfs.append(gdf)
    return pd.concat(gdfs, ignore_index=True)

def apply_ausblenden(
    gdf: gpd.GeoDataFrame,
    gpkg_path: str,
    config: dict,
    spezialmodus: bool
) -> gpd.GeoDataFrame:
    """
    Wendet das Ausblenden an, wenn aktiviert.
    """
    if not (spezialmodus and config.get("ausblenden", {}).get("aktiv", False)):
        return gdf

    aus_cfg = select_ausblendbereiche(gpkg_path, config["hauptland"])
    if not aus_cfg["aktiv"]:
        return gdf

    # alle ausgeblendeten Namen aus allen Layern sammeln
    verboten = set()
    for names in aus_cfg["bereiche"].values():
        verboten.update(names)

    return gdf[~gdf["NAME_1"].isin(verboten)]

def select_highlights(
    gdf: gpd.GeoDataFrame,
    gpkg_path: str,
    config: dict,
    spezialmodus: bool
) -> dict:
    """
    Führt die interaktive Hervorhebung durch oder
    liefert die statische Config zurück.
    """
    if not (spezialmodus and config.get("hervorhebung", {}).get("aktiv", False)):
        return {"aktiv": False, "layer": "", "namen": []}

    return select_highlight_regions(
        gpkg_path,
        config,
        verbotene_namen=None  # oder übergebe hier ausgeblendete Namen
    )