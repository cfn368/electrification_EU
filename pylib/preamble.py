# pylib/preamble.py

# --- third-party ---
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap

import requests
from scipy import stats
from scipy.stats import gaussian_kde
import statsmodels.formula.api as smf
from pylib import var_groups
from pylib.fetches import fetch, fetch_gva, fetch_energy_weights

try:
    import win32clipboard
except ImportError:
    win32clipboard = None

# --- stdlib ---
import itertools
from pathlib import Path
from typing import Sequence


def enable_autoreload(mode: int = 2) -> None:
    """Enable IPython autoreload (call from a notebook)."""
    ip = get_ipython()  # noqa: F821
    ip.run_line_magic("load_ext", "autoreload")
    ip.run_line_magic("autoreload", str(mode))


__all__ = [
    "np", "pd", "plt", "mcolors", "MaxNLocator", "requests",
    "itertools", "Path", "Sequence",
    "Patch", "Line2D", "LinearSegmentedColormap",
    "enable_autoreload", "var_groups", "fetch", "fetch_gva", "fetch_energy_weights",
]