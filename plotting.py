# plotting.py

import os
import matplotlib.pyplot as plt
from datetime import datetime


def plot_map(
    haupt_gdf,
    neben_gdfs,
    highlight_cfg: dict,
    colors: dict,
    bbox: tuple,
    width_px: int,
    height_px: int
):
    """
    Zeichnet Hauptland, Nebenländer und (optional) Highlights
    in eine Matplotlib-Figur und gibt (fig, ax) zurück.
    """
    dpi = 100
    figsize = (width_px / dpi, height_px / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Nebenländer
    for gdf in neben_gdfs:
        gdf.plot(ax=ax, color=colors["nebenland"], edgecolor=colors["grenze"])

    # Hauptland
    haupt_gdf.plot(ax=ax, color=colors["hauptland"], edgecolor=colors["grenze"])

    # Hervorhebung
    if highlight_cfg.get("aktiv") and highlight_cfg.get("namen"):
        gdf_highlight = haupt_gdf[
            haupt_gdf["NAME_1"].isin(highlight_cfg["namen"])
        ]
        gdf_highlight.plot(
            ax=ax,
            color=colors["highlight"],
            edgecolor=colors["grenze"]
        )

    ax.set_xlim(bbox[0], bbox[1])
    ax.set_ylim(bbox[2], bbox[3])
    ax.axis("off")

    return fig, ax


def save_map(
    fig,
    output_dir: str,
    region: str,
    crs: str,
    width_px: int,
    height_px: int,
    export_formats: set[str] = {"png"}  # Default
):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base = f"{region}_{crs.replace(':','_')}_{timestamp}"

    for ext in export_formats:
        filepath = os.path.join(output_dir, f"{base}.{ext}")
        if ext == "png":
            fig.savefig(
                filepath,
                dpi=100,
                transparent=True,
                bbox_inches=None,
                pad_inches=0
            )
        elif ext == "svg":
            fig.savefig(
                filepath,
                format="svg",
                bbox_inches=None,
                pad_inches=0
            )
        print(f"Karte gespeichert: {filepath}")

    plt.close(fig)