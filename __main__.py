#!/usr/bin/env python3
# __main__.py

import os
import sys
import logging
from rich.logging import RichHandler
from tqdm import tqdm

from config import load_config
from cli import (
    choose_mode,
    choose_region,
    choose_export_formats,
    choose_scalebar_option,
)
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
    # 1) Konfiguration laden
    config = load_config()

    # 2) Logging konfigurieren
    log_level_str = config.get("logging", {}).get("level", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    handlers = [RichHandler(rich_tracebacks=True)]
    if logfile := config.get("logging", {}).get("file"):
        fh = logging.FileHandler(logfile, encoding="utf-8")
        fh.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%H:%M:%S",
        ))
        handlers.append(fh)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )
    logger = logging.getLogger("mymaptool.main")

    try:
        # 3) Basis-Pfade
        base_dir = os.path.dirname(os.path.abspath(__file__))
        hauptland_dir = os.path.join(base_dir, "hauptland")
        nebenlaender_dir = os.path.join(base_dir, "nebenlaender")
        output_dir = os.path.join(
            base_dir,
            config.get("output_dir", "output")
        )
        os.makedirs(output_dir, exist_ok=True)

        # 4) Modus & Region wählen
        spezialmodus = choose_mode()
        region, ziel_crs_list = choose_region(config)

        # 5) Scalebar-Konfiguration
        scalebar_cfg = config.get(
            "scalebar", {"show": True, "position": "bottom-left"}
        )
        if spezialmodus:
            scalebar_cfg = choose_scalebar_option()

        # 6) Export-Formate
        export_formats = {"png"}
        if spezialmodus:
            export_formats = choose_export_formats()

        # 7) GPKG-Dateien finden
        haupt_gpkg_path, neben_gdfs = find_gpkg_files(
            hauptland_dir,
            nebenlaender_dir,
            config.get("nebenlaender", []),
        )

        # 8) Layer-Auswahl
        haupt_layers = (
            get_layers_interactive(haupt_gpkg_path)
            if spezialmodus
            else config.get("hauptland", [])
        )

        # 9) Geodaten verarbeiten
        gdf_haupt = merge_hauptland_layers(haupt_gpkg_path, haupt_layers)
        gdf_haupt, ausgeblendet_namen = apply_ausblenden(
            gdf_haupt,
            haupt_gpkg_path,
            haupt_layers,
            spezialmodus,
        )
        logger.debug(f"Ausgeblendete Regionen: {ausgeblendet_namen}")

        highlight_cfg = select_highlights(
            haupt_gpkg_path,
            config,
            haupt_layers,
            spezialmodus,
            ausgeblendet_namen,
        )

        # 10) Plot-Parameter
        breite_px = config["karte"]["breite"]
        hoehe_px = config["karte"]["hoehe"]
        aspect_ratio = breite_px / hoehe_px

        # 11) Rendering & Speichern
        for ziel_crs in tqdm(ziel_crs_list, desc="Projektionen"):
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
                scalebar_cfg=scalebar_cfg,
            )

            save_map(
                fig,
                output_dir,
                region,
                ziel_crs,
                breite_px,
                hoehe_px,
                export_formats,
            )

        logger.info("Alle Karten wurden erfolgreich erstellt.")

    except Exception as e:
        logger.exception("Fehler in main(): %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()