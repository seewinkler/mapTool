# data_processing/layers.py

import pandas as pd
import geopandas as gpd

from ausblenden import select_ausblendbereiche
from highlight_selector import select_highlight_regions

def merge_hauptland_layers(
    gpkg_path: str,
    layers: list[str]
) -> gpd.GeoDataFrame:
    """Alle angegebenen Layers einlesen und vereinen."""
    gdfs = [gpd.read_file(gpkg_path, layer=layer) for layer in layers]
    return pd.concat(gdfs, ignore_index=True)


def apply_ausblenden(
    gdf: gpd.GeoDataFrame,
    gpkg_path: str,
    verwendete_layers: list[str],
    spezialmodus: bool
) -> tuple[gpd.GeoDataFrame, set[str]]:
    """
    Im Spezialmodus interaktiv Admin-Gebiete zum Ausblenden wählen,
    Filter anwenden und die ausgeschlossenen Namen zurückgeben.
    """
    if not spezialmodus:
        return gdf, set()

    aus_cfg = select_ausblendbereiche(gpkg_path, verwendete_layers)
    if not aus_cfg["aktiv"]:
        return gdf, set()

    # Set ausgeblendeter NAME_1-Werte
    verboten = set()
    for names in aus_cfg["bereiche"].values():
        verboten.update(names)

    # GeoDataFrame filtern
    gdf_filtered = gdf[~gdf["NAME_1"].isin(verboten)]
    return gdf_filtered, verboten


def select_highlights(
    gpkg_path: str,
    config: dict,
    verwendete_layers: list[str],
    spezialmodus: bool,
    verbotene_namen: set[str]
) -> dict:
    """
    Im Spezialmodus interaktiv Admin-Gebiete zur Hervorhebung wählen,
    wobei bereits ausgeblendete Namen ausgeschlossen werden.
    """
    if not spezialmodus:
        return {"aktiv": False, "layer": "", "namen": []}

    return select_highlight_regions(
        gpkg_path,
        config,
        verbotene_namen=verbotene_namen
    )