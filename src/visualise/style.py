"""
Publication-quality plotting configuration.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl

# Colour palette
PALETTE = {
    "communicable": "#2166AC",   # Blue
    "ncd": "#B2182B",            # Red
    "injuries": "#F4A582",       # Salmon
    "highlight": "#1B7837",      # Green
    "neutral": "#636363",        # Grey
    "over": "#D6604D",           # Over-studied red
    "under": "#4393C3",          # Under-studied blue
    "covid": "#FDB863",          # COVID amber
}

LEVEL1_COLORS = {
    "Communicable, maternal, neonatal, and nutritional diseases": PALETTE["communicable"],
    "Non-communicable diseases": PALETTE["ncd"],
    "Injuries": PALETTE["injuries"],
}

LEVEL2_COLORS = {
    "Neoplasms": "#B2182B",
    "Cardiovascular diseases": "#D6604D",
    "Neurological disorders": "#F4A582",
    "Diabetes and kidney diseases": "#FDDBC7",
    "Mental disorders": "#92C5DE",
    "Respiratory infections and tuberculosis": "#2166AC",
    "Neglected tropical diseases and malaria": "#053061",
    "Sense organ diseases": "#F7F7F7",
    "Musculoskeletal disorders": "#E0E0E0",
    "Other": "#BDBDBD",
}


def set_lancet_style():
    """Apply publication-quality matplotlib settings."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 9,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "lines.linewidth": 1.2,
    })
