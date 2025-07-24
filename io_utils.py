import os
import geopandas as gpd
from typing import Tuple, List  # Großbuchstaben!

def find_gpkg_files(config: dict) -> Tuple[str, List[gpd.GeoDataFrame]]:
    """
    Sucht und lädt die GPKG-Dateien für Haupt- und Nebenländer.
    Gibt zurück: (pfad_haupt_gpkg, [GeoDataFrame_nebenlaender...])
    """
    haupt_dir = config["pfade"]["hauptland"]
    neben_dir = config["pfade"]["nebenlaender"]

    # Erstes GPKG im Hauptverzeichnis finden
    haupt_files = [f for f in os.listdir(haupt_dir) if f.endswith(".gpkg")]
    if not haupt_files:
        raise FileNotFoundError(f"Keine .gpkg im Verzeichnis {haupt_dir}")
    haupt_path = os.path.join(haupt_dir, haupt_files[0])

    # Alle Nebenländer-Dateien laden
    neben_gdfs = []
    for fname in os.listdir(neben_dir):
        if fname.endswith(".gpkg"):
            pfad = os.path.join(neben_dir, fname)
            # Hier geht’s davon aus, dass in config["nebenlaender"] der Layername steht
            gdf = gpd.read_file(pfad, layer=config["nebenlaender"])
            neben_gdfs.append(gdf)

    return haupt_path, neben_gdfs