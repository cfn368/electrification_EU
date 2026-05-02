"""
Fetches — Eurostat SDMX 2.1 data fetchers for the electrification analysis
===========================================================================

Fetches electrification rates, GVA, and energy balance data from Eurostat.
Used by 1_fetch.ipynb to build the intermediate Parquet files in 0_intermediate/.

Data sources:
    nrg_ind_re   — electricity share (%) of final consumption by sector
    nama_10_a64  — gross value added by NACE A64 industry (CP_MEUR)
    nrg_bal_c    — energy by sector and balance code (SIEC=TOTAL, E7000, green sources; TJ)
"""

import xml.etree.ElementTree as ET

import requests
import pandas as pd

from pylib import var_groups


# ==================== ==================== ==================== ====================
# 0. Internal constants and XML helper

_G = "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"

_BASE_ELEC = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_re"
_BASE_GVA  = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nama_10_a64"
_BASE_ENW  = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_bal_c"
_GVA_COUNTRIES = [c for c in var_groups.countries if c != 'EU28']

_H49_TARGETS = ['FC_TRA_RAIL_E', 'FC_TRA_ROAD_E', 'FC_TRA_PIPE_E']
_H5X_MAP     = {'H50': 'FC_TRA_DNAVI_E', 'H51': 'FC_TRA_DAVI_E'}
_C24_TARGETS = ['FC_IND_IS_E', 'FC_IND_NFM_E']


def _parse(r) -> pd.DataFrame:
    """Parse a Eurostat SDMX 2.1 generic XML response into a long DataFrame."""
    r.raise_for_status()
    root = ET.fromstring(r.text)
    rows = []
    for series in root.iter(f"{{{_G}}}Series"):
        sk = series.find(f"{{{_G}}}SeriesKey")
        dims = {v.get('id'): v.get('value') for v in sk.findall(f"{{{_G}}}Value")}
        for obs in series.iter(f"{{{_G}}}Obs"):
            year   = obs.find(f"{{{_G}}}ObsDimension").get('value')
            val_el = obs.find(f"{{{_G}}}ObsValue")
            val    = float(val_el.get('value')) if val_el is not None else None
            rows.append({**dims, 'year': int(year), 'value': val})
    return pd.DataFrame(rows)


# ==================== ==================== ==================== ====================
# 1. Fetch functions

def fetch(nrg_bal, countries=var_groups.countries, freq='A', start='1995') -> pd.DataFrame:
    """Electricity share (% of final consumption) by sector — nrg_ind_re.
    Key order: freq.nrg_bal.unit.geo  (unit is always PC).
    """
    nrg_bal_key = '+'.join(nrg_bal) if isinstance(nrg_bal, list) else nrg_bal
    key = f"{freq}.{nrg_bal_key}.PC.{'+'.join(countries)}"
    df = _parse(requests.get(f"{_BASE_ELEC}/{key}?startPeriod={start}"))
    df['label'] = df['nrg_bal'].map(var_groups.labels)
    return df


def fetch_gva(countries=_GVA_COUNTRIES, freq='A', start='1995') -> pd.DataFrame:
    """Gross value added by NACE A64 industry (CP_MEUR) — nama_10_a64.
    EU28 excluded. H49 split equally across rail/road/pipeline; H50→navigation; H51→aviation.
    """
    key = f"{freq}.CP_MEUR..B1G.{'+'.join(countries)}"
    df = _parse(requests.get(f"{_BASE_GVA}/{key}?startPeriod={start}"))

    df['nrg_bal'] = df['nace_r2'].map(var_groups.nace_to_nrg)

    extra_rows = []

    c24 = df[df['nace_r2'] == 'C24'].copy()
    for target in _C24_TARGETS:
        chunk = c24.copy()
        chunk['nrg_bal'] = target
        chunk['value']   = chunk['value'] / len(_C24_TARGETS)
        extra_rows.append(chunk)

    h49 = df[df['nace_r2'] == 'H49'].copy()
    for target in _H49_TARGETS:
        chunk = h49.copy()
        chunk['nrg_bal'] = target
        chunk['value']   = chunk['value'] / len(_H49_TARGETS)
        extra_rows.append(chunk)

    for code, target in _H5X_MAP.items():
        chunk = df[df['nace_r2'] == code].copy()
        chunk['nrg_bal'] = target
        extra_rows.append(chunk)

    df = df[~df['nace_r2'].isin(['C24', 'H49', 'H50', 'H51'])]
    if extra_rows:
        df = pd.concat([df] + extra_rows, ignore_index=True)

    df['label'] = df['nrg_bal'].map(var_groups.labels)
    return df


def fetch_energy_weights(sectors=None, countries=var_groups.countries, freq='A', start='1995') -> pd.DataFrame:
    """Total final energy consumption by sector (TJ) — nrg_bal_c, SIEC=TOTAL.
    Defaults to var_groups.subs if sectors is None.
    """
    if sectors is None:
        sectors = var_groups.subs
    nrg_key = '+'.join(sectors) if isinstance(sectors, list) else sectors
    key = f"{freq}.{nrg_key}.TOTAL.TJ.{'+'.join(countries)}"
    df = _parse(requests.get(f"{_BASE_ENW}/{key}?startPeriod={start}"))
    df['label'] = df['nrg_bal'].map(var_groups.labels)
    return df


def fetch_elec_consumption(sectors=None, countries=var_groups.countries, freq='A', start='1995') -> pd.DataFrame:
    """Electricity consumption by sector (TJ) — nrg_bal_c, SIEC=E7000.
    Defaults to var_groups.subs if sectors is None.
    """
    if sectors is None:
        sectors = var_groups.subs
    nrg_key = '+'.join(sectors) if isinstance(sectors, list) else sectors
    key = f"{freq}.{nrg_key}.E7000.TJ.{'+'.join(countries)}"
    df = _parse(requests.get(f"{_BASE_ENW}/{key}?startPeriod={start}"))
    df['label'] = df['nrg_bal'].map(var_groups.labels)
    return df


def fetch_greenpower(balance='GIC', countries=var_groups.countries, start='1995') -> tuple:
    """Green source and total energy (TJ) from nrg_bal_c for GIC or GEP.
    Returns (df_green, df_total) where df_green carries a 'label' from var_groups.GREEN_SOURCES.
    balance: 'GIC' (gross inland consumption) or 'GEP' (gross electricity production).
    """
    siec_key = '+'.join(var_groups.GREEN_SOURCES.keys())
    geo_key  = '+'.join(countries)
    df_green = _parse(requests.get(f"{_BASE_ENW}/A.{balance}.{siec_key}.TJ.{geo_key}?startPeriod={start}"))
    df_green['label'] = df_green['siec'].map(var_groups.GREEN_SOURCES)
    df_total = _parse(requests.get(f"{_BASE_ENW}/A.{balance}.TOTAL.TJ.{geo_key}?startPeriod={start}"))
    df_total = df_total[['geo', 'year', 'value']].rename(columns={'value': 'total_tj'})
    return df_green, df_total
