# scalebar.py

import numpy as np
from matplotlib.transforms import blended_transform_factory
from pyproj import CRS, Transformer
from config import SCALER

def pixel_to_pt(pixel, dpi):
    return pixel * 72 / dpi

def nice_number(x):
    if x <= 0:
        return 0
    exp = np.floor(np.log10(x))
    f   = x / 10**exp
    if f < 1.5:  nice_f = 1
    elif f < 3:  nice_f = 2
    elif f < 7:  nice_f = 5
    else:        nice_f = 10
    return nice_f * 10**exp

def add_scalebar(ax, extent, src_crs, label=None):
    # scalebar‐Einstellungen aus Config
    show            = SCALER.get("show", True)
    length_fraction = SCALER.get("length_fraction", 0.05)
    tick_fraction   = SCALER.get("tick_fraction", 0.02)
    position        = SCALER.get("position", "bottom-left")
    color           = SCALER.get("color", "white")
    linewidth_px    = SCALER.get("linewidth_px", 1.5)
    font_px         = SCALER.get("font_px", 8)

    if not show:
        return

    # 1) Extent → Meter (EPSG:3857)
    crs_obj = CRS.from_user_input(src_crs)
    if crs_obj.is_geographic:
        transformer = Transformer.from_crs(crs_obj, "EPSG:3857", always_xy=True)
        xmin, ymin = transformer.transform(extent[0], extent[2])
        xmax, ymax = transformer.transform(extent[1], extent[3])
    else:
        xmin, xmax, ymin, ymax = extent

    # 2) Pixel → pt
    dpi   = ax.figure.dpi
    lw_pt = pixel_to_pt(linewidth_px, dpi)
    fs_pt = pixel_to_pt(font_px, dpi)

    # 3) rohe Länge → „schöne“ Länge
    map_width = xmax - xmin
    raw_len   = map_width * length_fraction
    nice_len  = nice_number(raw_len)
    frac      = nice_len / map_width

    # 4) Label‐Fallback
    if label is None:
        label = f"{int(round(nice_len/1000))} km" if nice_len >= 1000 else f"{int(round(nice_len))} m"

    # 5) Position in Achsen‐Koords
    pos_map = {
        "bottom-left":   (0.05, 0.05),
        "bottom-center": (0.45, 0.05),
        "bottom-right":  (0.85, 0.05),
    }
    x0, y0 = pos_map.get(position, pos_map["bottom-left"])
    trans   = blended_transform_factory(ax.transAxes, ax.transAxes)

    # 6) Zeichnen
    ax.plot([x0, x0 + frac], [y0, y0], transform=trans,
            color=color, lw=lw_pt, zorder=5)

    tick = tick_fraction * frac
    for xx in (x0, x0 + frac):
        ax.plot([xx, xx], [y0, y0 + tick], transform=trans,
                color=color, lw=lw_pt, zorder=5)

    ax.text(x0 + frac/2, y0 + tick * 1.5, label, transform=trans,
            ha="center", va="bottom", fontsize=fs_pt, color=color,
            zorder=5)