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
    scalebar_cfg: dict = None,
    background_cfg: dict = None
):
    """
    Zeichnet bereits reprojizierte GeoDataFrames mit optionaler Scalebar
    und Hintergrund-Option (Farbfüllung oder transparent).

    haupt_gdf     – GeoDataFrame des Hauptgebiets (in Meter-CRS)
    neben_gdfs    – Liste von GeoDataFrames der Nebenländer (in Meter-CRS)
    highlight_cfg – Dict mit keys 'aktiv' (bool) und 'namen' (List[str])
    colors        – Dict mit keys 'hauptland','nebenland','grenze','highlight'
    bbox          – (xmin, xmax, ymin, ymax) in selben CRS-Einheiten
    width_px      – Bildbreite in Pixel
    height_px     – Bildhöhe in Pixel
    scalebar_cfg  – Dict mit Scalebar-Optionen: show (bool), position (str),
                     length_fraction (float), color (str),
                     linewidth (float), fontsize (int)
    background_cfg– Dict mit keys 'color' (Hex-String) und 'transparent' (bool).
                     Wenn None: Hintergrund transparent.
    """
    dpi     = 100
    figsize = (width_px / dpi, height_px / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # 0) Hintergrund setzen (Fallback: transparent)
    if background_cfg:
        bg_color  = background_cfg.get("color", "#2896BA")
        bg_transp = background_cfg.get("transparent", False)
    else:
        bg_color  = "none"
        bg_transp = True

    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    if bg_transp:
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
    else:
        fig.patch.set_alpha(1)
        ax.patch.set_alpha(1)

    # 1) Nebenländer zeichnen
    for g in neben_gdfs:
        g.plot(
            ax=ax,
            color=colors["nebenland"],
            edgecolor=colors["grenze"]
        )

    # 2) Hauptland zeichnen
    haupt_gdf.plot(
        ax=ax,
        color=colors["hauptland"],
        edgecolor=colors["grenze"]
    )

    # 3) Hervorhebung zeichnen
    if highlight_cfg.get("aktiv") and highlight_cfg.get("namen"):
        mask = haupt_gdf["NAME_1"].isin(highlight_cfg["namen"])
        haupt_gdf[mask].plot(
            ax=ax,
            color=colors["highlight"],
            edgecolor=colors["grenze"]
        )

    # 4) Ansicht beschneiden und Achsen ausblenden
    xmin, xmax, ymin, ymax = bbox
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.axis("off")

    # 5) Scalebar hinzufügen
    if scalebar_cfg and scalebar_cfg.get("show", False):
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
    export_formats: set[str] = {"png"},
    background_cfg: dict = None
):
    """
    Speichert die Karte in exakt den Pixelmaßen (width_px × height_px),
    ohne äußere Ränder, im angegebenen Ausgabeordner.

    Dateiname: {region}_{crs}_{timestamp}.{ext}
    """

    # Timestamp und Basis-Pfad
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base = f"{region}_{crs.replace(':','_')}_{timestamp}"

    # Konstantes DPI
    dpi = 100

    # Figure-Größe in Zoll so setzen, dass dpi * Zoll = gewünschte Pixelgröße
    fig.set_size_inches(width_px / dpi, height_px / dpi)

    # Subplots so strecken, dass Achsen exakt die Figure füllen
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Achsen-Bounding-Box in Zoll berechnen
    ax = fig.axes[0] if fig.axes else None
    if ax:
        bbox_inches = (
            ax.get_window_extent()
               .transformed(fig.dpi_scale_trans.inverted())
        )
    else:
        bbox_inches = None

    # Transparenz-Option: default transparent, außer explizit anders gesetzt
    if background_cfg:
        transparent = background_cfg.get("transparent", False)
    else:
        transparent = True

    # Schleife über die gewünschten Formate
    for ext in export_formats:
        filepath = os.path.join(output_dir, f"{base}.{ext}")

        if ext.lower() == "png":
            fig.savefig(
                filepath,
                dpi=dpi,
                transparent=transparent,
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

    # Aufräumen
    plt.close(fig)