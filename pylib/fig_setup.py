"""
Fig setup — matplotlib style and shared figure helpers
======================================================

Applies AEJ-style rcParams at import time. Exposes PALETTE, STYLE, LW, and
SEC_PALETTE for country/sector coloring, and three helper functions used
across all notebooks.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from cycler import cycler

from pylib.var_groups import country_names


# ==================== ==================== ==================== ====================
# 0. rcParams

BASE = 9

mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": [
        "DejaVu Serif",
        "TeX Gyre Pagella",
        "Palatino Linotype",
        "Book Antiqua",
        "URW Palladio L",
    ],
    "font.sans-serif": ["DejaVu Sans"],
    "font.style": "italic",
    "mathtext.fontset": "dejavuserif",
    "mathtext.default": "regular",
    "text.usetex": False,
    "axes.unicode_minus": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "axes.prop_cycle": cycler(color=["#FF0000", "#374151", "#003A8C"]),
    "axes.facecolor": "#EAF1F2",
    "figure.facecolor": "#EAF1F2",
    "axes.spines.top": False,
    "axes.spines.right": False,
    'axes.spines.left': False,
    'axes.spines.bottom': False,
    "axes.grid.axis": "y",
    "grid.color": "white",
    "grid.linewidth": 1,
})

mpl.rcParams.update({
    "font.size":             BASE,
    "figure.titlesize":      BASE + 9,
    "axes.titlesize":        BASE + 7,
    "axes.labelsize":        BASE + 7,
    "xtick.labelsize":       BASE + 6,
    "ytick.labelsize":       BASE + 3,
    "legend.fontsize":       BASE + 7,
    "legend.title_fontsize": BASE + 7,
})


# ==================== ==================== ==================== ====================
# 1. Colour constants

PALETTE = {
    "DK":        "#E04131",
    "SE":        "#DE7626",
    "NO":        "#18DBB1",
    "DE":        "#000000",
    "NL":        "#A16D45",
    # "ES":        "#63110A",
    "FR":        "#090BDF",
    # "UK":        "#34BA5B",
    "FI":        "#7B81E0",
    "EU27_2020": "#275C51",
}

STYLE = {geo: "--" if geo == "EU27_2020" else "-"  for geo in PALETTE}
LW    = {geo: 2.2   if geo == "EU27_2020" else 1.6 for geo in PALETTE}

# 20-color palette for sector charts: project colors + 10 complementary
SEC_PALETTE = [
    "#E04131", "#DE7626", "#18DBB1", "#6A7015", "#5E3F27",
    "#63110A", "#090BDF", "#34BA5B", "#7B81E0", "#275C51",
    "#F5C518", "#C084FC", "#FB7185", "#38BDF8", "#EBD87C",
    "#4ADE80", "#FB923C", "#818CF8", "#A3E635", "#34D399",
]


# ==================== ==================== ==================== ====================
# 2. Shared helpers

def style_ax(ax, years, step=5):
    """Grid, tight xlim, clean x ticks, y-tick dash format."""
    ax.grid(axis="y")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x:.0f} -")
    )
    ax.set_xlim(years.min(), years.max())
    y0, y1 = int(years.min()), int(years.max())
    ax.xaxis.set_major_locator(
        mticker.FixedLocator(
            range(y0 + (step - y0 % step) % step, y1 + 1, step)
        )
    )


def legend(ax, **kwargs):
    """Framed, rounded-corner legend."""
    defaults = dict(frameon=True, framealpha=0.95, edgecolor="0.5", fancybox=True)
    return ax.legend(**{**defaults, **kwargs})


def country_handles(countries):
    """Legend handles for a list of country codes."""
    return [
        plt.Line2D([0], [0], color=PALETTE[g], ls=STYLE[g], lw=LW[g],
                   label=country_names.get(g, g))
        for g in countries
    ]
