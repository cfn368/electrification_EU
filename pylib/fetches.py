import xml.etree.ElementTree as ET
import requests
import pandas as pd
from pylib import var_groups

_G = "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"

_BASE_ELEC = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_re"
_BASE_GVA  = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nama_10_a64"
_BASE_ENW  = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_bal_c"
_GVA_COUNTRIES = [c for c in var_groups.countries if c != 'EU28']

# H49 split equally across land transport subsectors; H50/H51 direct
_H49_TARGETS = ['FC_TRA_RAIL_E', 'FC_TRA_ROAD_E', 'FC_TRA_PIPE_E']
_H5X_MAP     = {'H50': 'FC_TRA_DNAVI_E', 'H51': 'FC_TRA_DAVI_E'}

# C24 split equally across iron & steel and non-ferrous metals (inseparable in NACE A64)
_C24_TARGETS = ['FC_IND_IS_E', 'FC_IND_NFM_E']


def _parse(r) -> pd.DataFrame:
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


def fetch(nrg_bal, countries=var_groups.countries, freq='A', start='1995') -> pd.DataFrame:
    """Electricity share (% of final consumption) by sector — Eurostat nrg_ind_re.
    Key order: freq.nrg_bal.unit.geo  (unit is always PC).
    """
    nrg_bal_key = '+'.join(nrg_bal) if isinstance(nrg_bal, list) else nrg_bal
    key = f"{freq}.{nrg_bal_key}.PC.{'+'.join(countries)}"
    df = _parse(requests.get(f"{_BASE_ELEC}/{key}?startPeriod={start}"))
    df['label'] = df['nrg_bal'].map(var_groups.labels)
    return df


def fetch_gva(countries=_GVA_COUNTRIES, freq='A', start='1995') -> pd.DataFrame:
    """Gross value added by NACE A64 industry (CP_MEUR) — Eurostat nama_10_a64.
    Key order: freq.unit.nace_r2.na_item.geo  (unit=CP_MEUR, na_item=B1G).
    EU28 excluded. H49 split equally across rail/road/pipeline; H50→navigation; H51→aviation.
    """
    key = f"{freq}.CP_MEUR..B1G.{'+'.join(countries)}"
    df = _parse(requests.get(f"{_BASE_GVA}/{key}?startPeriod={start}"))

    # Standard nace_to_nrg mapping (excludes H49/H50/H51)
    df['nrg_bal'] = df['nace_r2'].map(var_groups.nace_to_nrg)

    extra_rows = []

    # C24 → equal split across iron & steel and non-ferrous metals (inseparable in A64)
    c24 = df[df['nace_r2'] == 'C24'].copy()
    for target in _C24_TARGETS:
        chunk = c24.copy()
        chunk['nrg_bal'] = target
        chunk['value']   = chunk['value'] / len(_C24_TARGETS)
        extra_rows.append(chunk)

    # H49 → equal split across rail, road, pipeline
    h49 = df[df['nace_r2'] == 'H49'].copy()
    for target in _H49_TARGETS:
        chunk = h49.copy()
        chunk['nrg_bal'] = target
        chunk['value']   = chunk['value'] / len(_H49_TARGETS)
        extra_rows.append(chunk)

    # H50 → domestic navigation, H51 → domestic aviation
    for code, target in _H5X_MAP.items():
        chunk = df[df['nace_r2'] == code].copy()
        chunk['nrg_bal'] = target
        extra_rows.append(chunk)

    # Drop split codes from main df (replaced by extra_rows)
    df = df[~df['nace_r2'].isin(['C24', 'H49', 'H50', 'H51'])]
    if extra_rows:
        df = pd.concat([df] + extra_rows, ignore_index=True)

    df['label'] = df['nrg_bal'].map(var_groups.labels)
    return df


def fetch_energy_weights(sectors=None, countries=var_groups.countries, freq='A', start='1995') -> pd.DataFrame:
    """Total final energy consumption by sector (TJ) — Eurostat nrg_bal_c.
    Key order: freq.nrg_bal.siec.unit.geo  (siec=TOTAL, unit=TJ).
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
    """Electricity consumption by sector (TJ) — Eurostat nrg_bal_c.
    Key order: freq.nrg_bal.siec.unit.geo  (siec=E7000, unit=TJ).
    Defaults to var_groups.subs if sectors is None.
    """
    if sectors is None:
        sectors = var_groups.subs
    nrg_key = '+'.join(sectors) if isinstance(sectors, list) else sectors
    key = f"{freq}.{nrg_key}.E7000.TJ.{'+'.join(countries)}"
    df = _parse(requests.get(f"{_BASE_ENW}/{key}?startPeriod={start}"))
    df['label'] = df['nrg_bal'].map(var_groups.labels)
    return df
