# plotting.py

import os
import logging
import matplotlib.pyplot as plt
from datetime import datetime
from scalebar import add_scalebar

logger = logging.getLogger("mymaptool.plotting")


def plot_map(
    haupt_gdf,
    neben_gdfs,
    highlight_cfg: dict,
    colors: dict,
    bbox: tuple,
    width_px: int,
    height_px: int,
    scalebar_cfg: dict = None
):
    """
    Zeichnet bereits reprojizierte GeoDataFrames mit optionaler Scalebar.
    
    haupt_gdf     – GeoDataFrame des Hauptgebiets (in Meter-CRS)
    neben_gdfs    – Liste von GeoDataFrames der Nebenländer (in Meter-CRS)
    highlight_cfg – Dict mit keys 'aktiv' (bool) und 'namen' (List[str])
    colors        – Dict mit keys 'hauptland','nebenland','grenze','highlight'
    bbox          – (xmin, xmax, ymin, ymax) in selben CRS-Einheiten
    width_px      – Bildbreite in Pixel
    height_px     – Bildhöhe in Pixel
    scalebar_cfg  – Dict mit Scalebar-Optionen:
                     show (bool), position (str),
                     length_fraction (float),
                     color (str), linewidth (float), fontsize (int)
    """
    dpi     = 100
    figsize = (width_px / dpi, height_px / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Nebenländer zeichnen
    for g in neben_gdfs:
        g.plot(ax=ax,
               color=colors["nebenland"],
               edgecolor=colors["grenze"])

    # Hauptland zeichnen
    haupt_gdf.plot(ax=ax,
                   color=colors["hauptland"],
                   edgecolor=colors["grenze"])

    # Hervorhebung zeichnen
    if highlight_cfg.get("aktiv") and highlight_cfg.get("namen"):
        mask = haupt_gdf["NAME_1"].isin(highlight_cfg["namen"])
        haupt_gdf[mask].plot(
            ax=ax,
            color=colors["highlight"],
            edgecolor=colors["grenze"]
        )

    # Ansicht beschneiden
    xmin, xmax, ymin, ymax = bbox
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.axis("off")

    # Scalebar hinzufügen
    if scalebar_cfg and scalebar_cfg.get("show", False):
        # Aktuelle Achsenlimits verwenden
        xmin_ax, xmax_ax = ax.get_xlim()
        ymin_ax, ymax_ax = ax.get_ylim()
        extent = [xmin_ax, xmax_ax, ymin_ax, ymax_ax]

        add_scalebar(
            ax,
            extent,
            src_crs=haupt_gdf.crs,
            length_fraction=scalebar_cfg.get("length_fraction", 0.1),
            position=scalebar_cfg.get("position", "bottom-left"),
            show=True,
            color=scalebar_cfg.get("color", "white"),
            linewidth=scalebar_cfg.get("linewidth", 1.5),
            fontsize=scalebar_cfg.get("fontsize", 8)
        )

    return fig, ax


def save_map(
    fig,
    output_dir: str,
    region: str,
    crs: str,
    width_px: int,
    height_px: int,
    export_formats: set[str] = {"png"}
):
    """
    Speichert die Karte in genau den Pixelmaßen (width_px × height_px),
    ohne äußere Ränder, im angegebenen Ausgabeordner.
    Dateiname: {region}_{crs}_{timestamp}.{ext}
    """
    # 1. Timestamp und Basis-Pfad
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base = f"{region}_{crs.replace(':','_')}_{timestamp}"

    # 2. Konstantes DPI
    dpi = 100

    # 3. Figure-Größe in Zoll so setzen, dass
    #    dpi * Zoll = gewünschte Pixelgröße
    fig.set_size_inches(width_px / dpi, height_px / dpi)

    # 4. Subplots so strecken, dass Achsen exakt die Figure füllen
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # 5. Achsen-Bounding-Box in Zoll berechnen
    #    (wir nehmen die erste Achse – bei mehreren ggfs. anpassen)
    ax = fig.axes[0] if fig.axes else None
    if ax:
        bbox_inches = ax.get_window_extent() \
                         .transformed(fig.dpi_scale_trans.inverted())
    else:
        bbox_inches = None

    # 6. Schleife über die gewünschten Formate
    for ext in export_formats:
        filepath = os.path.join(output_dir, f"{base}.{ext}")

        if ext.lower() == "png":
            fig.savefig(
                filepath,
                dpi=dpi,
                transparent=True,
                bbox_inches=bbox_inches,
                pad_inches=0
            )
        elif ext.lower() == "svg":
            fig.savefig(
                filepath,
                format="svg",
                bbox_inches=bbox_inches,
                pad_inches=0
            )
        else:
            logger.warning(f"Unbekanntes Format '{ext}' – übersprungen.")
            continue

        logger.info(f"Karte gespeichert: {filepath}")

    # 7. Aufräumen
    plt.close(fig)
