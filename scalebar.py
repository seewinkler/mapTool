# scalebar.py

import numpy as np
from matplotlib.transforms import blended_transform_factory
from pyproj import CRS, Transformer

def nice_number(x):
    if x <= 0:
        return 0
    exp = np.floor(np.log10(x))
    f   = x / 10**exp
    if f < 1.5:
        nice_f = 1
    elif f < 3:
        nice_f = 2
    elif f < 7:
        nice_f = 5
    else:
        nice_f = 10
    return nice_f * 10**exp

def add_scalebar(
    ax,
    extent,
    src_crs,
    length_fraction=0.07,
    position='bottom-left',
    show=True,
    color='white',
    linewidth=1.5,
    fontsize=8
):
    if not show:
        return

    # Bei geografischen Daten (nur falls du sie doch mal nutzt)
    crs_obj = CRS.from_user_input(src_crs)
    if crs_obj.is_geographic:
        # sicherheitshalber in Web-Mercator umrechnen
        transformer = Transformer.from_crs(crs_obj, "EPSG:3857", always_xy=True)
        xmin, ymin = transformer.transform(extent[0], extent[2])
        xmax, ymax = transformer.transform(extent[1], extent[3])
    else:
        xmin, xmax, ymin, ymax = extent

    # Länge & Position
    map_width = xmax - xmin
    raw_len   = map_width * length_fraction
    nice_len  = nice_number(raw_len)
    frac      = nice_len / map_width

    pos_map = {
        'bottom-left':   (0.05, 0.05),
        'bottom-center': (0.45, 0.05),
        'bottom-right':  (0.85, 0.05),
    }
    x0, y0 = pos_map.get(position, pos_map['bottom-left'])
    trans   = blended_transform_factory(ax.transAxes, ax.transAxes)

    # Linie & Ticks
    ax.plot([x0, x0+frac], [y0, y0], transform=trans, color=color, lw=linewidth, zorder=5)
    tick = 0.02 * frac
    for xx in (x0, x0+frac):
        ax.plot([xx, xx], [y0, y0+tick], transform=trans, color=color, lw=linewidth, zorder=5)

    # Beschriftung
    if nice_len >= 1000:
        label = f"{int(nice_len/1000)} km"
    else:
        label = f"{int(nice_len)} m"

    ax.text(x0 + frac/2, y0 + tick*1.5, label,
            transform=trans, ha='center', va='bottom',
            fontsize=fontsize, color=color, zorder=5)