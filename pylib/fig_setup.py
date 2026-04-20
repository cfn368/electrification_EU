# nice figures (Danish æ/ø/å-safe)
import matplotlib as mpl
from cycler import cycler

BASE = 9

mpl.rcParams.update({
    # --- fonts (pick ONE reliable unicode serif first) ---
    "font.family": "serif",
    "font.serif": [
        "DejaVu Serif",        # robust unicode incl. æ/ø/å
        "TeX Gyre Pagella",
        "Palatino Linotype",
        "Book Antiqua",
        "URW Palladio L",
    ],
    "font.sans-serif": ["DejaVu Sans"],  # fallback if something forces sans
    "mathtext.fontset": "dejavuserif",
    "mathtext.default": "regular",

    # --- rendering: make sure unicode text is used ---
    "text.usetex": False,        # MUST be False if you rely on unicode directly
    "axes.unicode_minus": False,

    # --- PDF/SVG export: embed fonts so glyphs survive ---
    "pdf.fonttype": 42,          # embed TrueType (keeps æ/ø/å)
    "ps.fonttype": 42,
    "svg.fonttype": "none",      # keep text as text in SVG (not paths)

    # colors (yours)
    "axes.prop_cycle": cycler(color=["#FF0000", "#374151", "#003A8C"]),
})

mpl.rcParams.update({
    "font.size": BASE,
    "figure.titlesize": BASE + 9,
    "axes.titlesize": BASE + 7,
    "axes.labelsize": BASE + 7,
    "xtick.labelsize": BASE + 6,
    "ytick.labelsize": BASE + 3,
    "legend.fontsize": BASE + 7,
    "legend.title_fontsize": BASE + 7,
})