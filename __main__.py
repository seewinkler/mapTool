# __main__.py

import os

from config import load_config
from cli import choose_mode, choose_region
from io_utils import find_gpkg_files
from layer_selector import get_layers_interactive
from data_processing.layers import (
    merge_hauptland_layers,
    apply_ausblenden,
    select_highlights,
)
from data_processing.crs import reproject, compute_bbox
from plotting import plot_map, save_map


def main():
    # 1) Konfiguration
    config = load_config()

    # 2) Basis-Pfade
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    hauptland_dir = os.path.join(BASE_DIR, "hauptland")
    nebenlaender_dir = os.path.join(BASE_DIR, "nebenlaender")
    output_dir = os.path.join(BASE_DIR, "output")

    # 3) Modus & Region
    spezialmodus = choose_mode()
    region, ziel_crs_list = choose_region(config)

    # 4) GPKG-Dateien holen
    haupt_gpkg_path, neben_gdfs = find_gpkg_files(
        hauptland_dir,
        nebenlaender_dir,
        config["nebenlaender"],
    )

    # 5) Layer-Auswahl für Hauptland
    if spezialmodus:
        haupt_layers = get_layers_interactive(haupt_gpkg_path)
    else:
        haupt_layers = config.get("hauptland", [])

    # 6) Hauptland zusammenführen
    gdf_haupt = merge_hauptland_layers(haupt_gpkg_path, haupt_layers)

    # nach apply_ausblenden …
    gdf_haupt, ausgeblendet_namen = apply_ausblenden(
        gdf_haupt,
        haupt_gpkg_path,
        haupt_layers,
        spezialmodus,
    )
    print("DEBUG – ausgeblendete Regionen:", ausgeblendet_namen)

    # 8) Hervorhebung auswählen (mit Ausschluss der ausgeblendeten Namen)
    highlight_cfg = select_highlights(
        haupt_gpkg_path,
        config,
        haupt_layers,
        spezialmodus,
        ausgeblendet_namen,
    )

    # 9) Plot-Parameter
    breite_px = config["karte"]["breite"]
    hoehe_px = config["karte"]["hoehe"]
    aspect_ratio = breite_px / hoehe_px

    # 10) Für jede Projektion Karte rendern & speichern
    for ziel_crs in ziel_crs_list:
        haupt_proj = reproject(gdf_haupt, ziel_crs)
        neben_proj = [reproject(g, ziel_crs) for g in neben_gdfs]
        bbox = compute_bbox(haupt_proj, aspect_ratio)

        fig, ax = plot_map(
            haupt_proj,
            neben_proj,
            highlight_cfg,
            config["farben"],
            bbox,
            breite_px,
            hoehe_px,
        )

        save_map(fig, output_dir, region, ziel_crs, breite_px, hoehe_px)


if __name__ == "__main__":
    main()