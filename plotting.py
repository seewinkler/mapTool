import matplotlib.pyplot as plt
from datetime import datetime
import os

def plot_map(haupt, neben_list, highlight_cfg, colors, bbox, aspect):
    fig, ax = plt.subplots(figsize=(colors["breite"]/100, colors["hoehe"]/100), dpi=100)
    for n in neben_list:
        n.plot(ax=ax, color=colors["nebenland"], edgecolor=colors["grenze"])
    haupt.plot(ax=ax, color=colors["hauptland"], edgecolor=colors["grenze"])
    if highlight_cfg:
        # ...
        pass
    ax.set_xlim(bbox[0], bbox[1]); ax.set_ylim(bbox[2], bbox[3])
    ax.axis("off")
    return fig, ax

def save_map(fig, out_dir, region, crs):
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base = f"map_{region}_{crs.replace(':','_')}_{ts}"
    for ext in ("png","svg"):
        path = os.path.join(out_dir, f"{base}.{ext}")
        fig.savefig(path, dpi=100, transparent=True if ext=="png" else False, pad_inches=0)
        print(f"→ {path}")
    plt.close(fig)