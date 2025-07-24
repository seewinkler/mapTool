from config import load_config
from cli import choose_mode, choose_region
from io_utils import find_gpkg_files
from data_processing.layers import (
    merge_hauptland_layers,
    apply_ausblenden,
    select_highlights,
)
from data_processing.crs import reproject, compute_bbox
from plotting import plot_map, save_map

def main():
    config = load_config("config.json")
    spezialmodus = choose_mode()
    region, ziel_crs_list = choose_region(config)

    gpkg_haupt, neben_gpkgs = find_gpkg_files(config)

    # Hauptland laden & vereinigen
    gdf_haupt = merge_hauptland_layers(gpkg_haupt, config, spezialmodus)

    # Ausblenden & Hervorheben
    gdf_haupt = apply_ausblenden(gdf_haupt, gpkg_haupt, config, spezialmodus)
    highlight_cfg = select_highlights(gdf_haupt, gpkg_haupt, config, spezialmodus)

    # Loop über Projektionen
    for crs in ziel_crs_list:
        haupt_proj = reproject(gdf_haupt, crs)
        neben_proj = [reproject(g, crs) for g in neben_gpkgs]
        bbox = compute_bbox(haupt_proj, config["karte"]["breite"] / config["karte"]["hoehe"])

        fig, ax = plot_map(
            haupt_proj,
            neben_proj,
            highlight_cfg,
            config["farben"],
            bbox,
            config["karte"]["breite"] / config["karte"]["hoehe"],
        )
        save_map(fig, config["output_path"], region, crs)

if __name__ == "__main__":
    main()