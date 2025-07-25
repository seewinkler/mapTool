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
    choose_dimensions,
    choose_scalebar_option,
    choose_background_option,
    choose_export_formats    
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
    config = load_config("config.json")

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
        # 3) Basis-Pfade anlegen
        base_dir = os.path.dirname(os.path.abspath(__file__))
        hauptland_dir = os.path.join(base_dir, "hauptland")
        nebenlaender_dir = os.path.join(base_dir, "nebenlaender")
        output_dir = os.path.join(base_dir, config.get("output_dir", "output"))
        os.makedirs(output_dir, exist_ok=True)

        # 4) Modus wählen
        spezialmodus = choose_mode()

        # 5) Region wählen
        region, ziel_crs_list = choose_region(config)

        # 6) Kartengröße bestimmen
        breite_px, hoehe_px = choose_dimensions(spezialmodus, config)

        # 7) Scalebar konfigurieren
        scalebar_cfg = config.get("scalebar", {"show": True, "position": "bottom-left"})
        if spezialmodus:
            scalebar_cfg = choose_scalebar_option()
            
       # 7) Background-Konfiguration
        background_cfg = config.get("background", {"color":"#2896BA","transparent":False})
        if spezialmodus:
            background_cfg = choose_background_option()

        # 8) GPKG-Dateien finden
        haupt_gpkg_path, neben_gdfs = find_gpkg_files(
            hauptland_dir,
            nebenlaender_dir,
            config.get("nebenlaender", []),
        )

        # 9) Layer-Auswahl
        if spezialmodus:
            haupt_layers = get_layers_interactive(haupt_gpkg_path)
        else:
            haupt_layers = config.get("hauptland", [])

        # 10) Geodaten verarbeiten
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

        # 11) Export-Formate wählen (erst jetzt, am Ende der Interaktion)
        export_formats = {"png"}
        if spezialmodus:
            export_formats = choose_export_formats()

        # 12) Karten erstellen & speichern
        aspect_ratio = breite_px / hoehe_px

        for ziel_crs in tqdm(ziel_crs_list, desc="Projektionen"):
            # reprojiziere
            haupt_proj = reproject(gdf_haupt, ziel_crs)
            neben_proj = [reproject(g, ziel_crs) for g in neben_gdfs]

            # Bounding Box passend zum Seitenverhältnis
            bbox = compute_bbox(haupt_proj, aspect_ratio)

            # Plotten
            fig, ax = plot_map(
                haupt_proj,
                neben_proj,
                highlight_cfg,
                config["farben"],
                bbox,
                breite_px,
                hoehe_px,
                scalebar_cfg=scalebar_cfg,
                background_cfg=background_cfg,
                linien_cfg=config.get("linien"),
            )

            # Speichern
            save_map(
                fig,
                output_dir,
                region,
                ziel_crs,
                breite_px,
                hoehe_px,
                export_formats,
                background_cfg=background_cfg,
            )

        logger.info("Alle Karten wurden erfolgreich erstellt.")

    except Exception as e:
        logger.exception("Fehler in main(): %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
