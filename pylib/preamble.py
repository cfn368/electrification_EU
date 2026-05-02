"""
Preamble — standard imports and helpers for analysis notebooks
==============================================================

Re-exports the full import surface used across all notebooks in this project.
Import this module at the top of each notebook instead of repeating imports.
"""

import itertools
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator
import requests
from scipy import stats
from scipy.stats import gaussian_kde
import statsmodels.formula.api as smf

try:
    import win32clipboard
except ImportError:
    win32clipboard = None

from pylib import var_groups
from pylib.fetches import fetch, fetch_gva, fetch_energy_weights, fetch_elec_consumption, fetch_greenpower


def enable_autoreload(mode: int = 2) -> None:
    """Enable IPython autoreload (call from a notebook)."""
    ip = get_ipython()  # noqa: F821
    ip.run_line_magic("load_ext", "autoreload")
    ip.run_line_magic("autoreload", str(mode))


__all__ = [
    "np", "pd", "plt", "mcolors", "MaxNLocator", "requests",
    "itertools", "Path", "Sequence",
    "Patch", "Line2D", "LinearSegmentedColormap",
    "enable_autoreload", "var_groups",
    "fetch", "fetch_gva", "fetch_energy_weights", "fetch_elec_consumption", "fetch_greenpower",
]
