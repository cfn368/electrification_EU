# Projektkontekst — elektrificering i EU

## Formål
Shift-share dekomponering af forskellen i elektrificeringsrate over tid og på tværs af lande.
Spørgsmålet er: skyldes forskelle i elektrificeringsrate branchespecifikke forbedringer (intensity effect)
eller ændringer i erhvervssammensætningen (composition/mix effect)?

## Data og pipeline

### Datafiler (0_intermediate/)
| Fil | Indhold |
|-----|---------|
| `df_a.parquet` | Aggregeret elektrificeringsrate pr. land og år |
| `df_m.parquet` | Elektrificeringsrate for 3 overordnede sektorer (industri, transport, øvrige) |
| `df_s.parquet` | Elektrificeringsrate for alle delsektorer (nrg_bal-koder) |
| `df.parquet` | Kombineret datasæt: elektrificeringsrate + energiforbrug (TJ) pr. land, år og delsektor |
| `df_enw.parquet` | Energiforbrug (TJ) pr. land, år og delsektor — bruges til dekomponeringsvægte |

### Hentning
- `1_fetch.ipynb` henter data fra Eurostat via `pylib/fetches.py`
- Elektricitetsforbrug/elektrificeringsrater: `nrg_bal_c` (Eurostat energy balances)
- Energivægte (TJ): `nrg_bal_c`, balance-post varierer pr. sektor, SIEC=TOTAL, enhed=TJ — via `fetch_energy_weights()`
- GVA-funktioner er beholdt i `fetches.py` men bruges ikke længere til dekomponeringen

### Lande (aktive i analysen)
`var_groups.countries` minus UK (dårlige data) og ES (ikke tilgængelig i energidatasæt):
**DK, SE, DE, NL, FR, FI, EU27_2020**

NO er kommenteret ud i `var_groups.countries` og indgår ikke i den aktive analyse.

EU27_2020 indgår som benchmark — GIC-andelene behøver ikke divideres med 27 i dekomponeringen (ratio går ud med sig selv).

### Ekskluderede sektorer
`FC_OTH_NSP_E`, `FC_TRA_NSP_E`, `FC_TRA_DAVI_E` (indenrigsluftfart), `FC_TRA_DNAVI_E` (indenrigssøfart)
— mangler meningsfulde energivægte eller er for små/støjende.
`FC_IND_IS_E` og `FC_IND_NFM_E` er **inkluderet** (energidata findes, ingen GVA-mapping nødvendig).

## Kodestruktur

### pylib/
| Fil | Indhold |
|-----|---------|
| `preamble.py` | Standardimports (pandas, numpy, matplotlib, var_groups m.m.) inkl. `fetch_energy_weights` |
| `fig_setup.py` | Figuropsætning: `PALETTE`, `STYLE`, `LW`, `SEC_PALETTE`, `style_ax()`, `country_handles()`, `legend()` |
| `var_groups.py` | Metadata: landekoder, sektorkoder, `labels` (dansk), `country_names`, `nace_map` |
| `fetches.py` | Datafetching: `fetch()`, `fetch_gva()`, `fetch_energy_weights()` (SIEC=TOTAL, TJ), `fetch_elec_consumption()` (SIEC=E7000, TJ) |

### Vigtige konventioner
- `style_ax(ax, years, step=5)` — sætter grid, xlim og x-tick-interval (brug `step=10` for tætte figurer)
- `country_handles(countries)` — returnerer legend-handles med fulde landenavne fra `var_groups.country_names`
- `SEC_PALETTE` — 20-farve palette til sektorfigurer (de første 10 er projektets standardfarver)
- Stablede søjlediagrammer: brug **altid** integer x-positioner (`np.arange`) + `.to_numpy()` + `.fillna(0)` — pandas categorical axis i matplotlib giver stille fejl
- Sektorrækkefølge fra Eurostat API er **alfabetisk** (ikke rækkefølgen i request-key) — brug `list(df.nrg_bal.unique())` til konsistent sortering på tværs af notebooks

## Notebooks

### 2_electrification_rates.ipynb
Deskriptiv analyse af elektrificeringsrater. Færdig.
- Fig 1–4: aggregeret rate og overordnede sektorer (absolut + indekseret)
- Fig 5: DK vs. EU27 på delsektorniveau, 4 kolonner, legend nedenunder

### 2_GVA.ipynb
GVA-datakvalitetskontrol. Beholdt som reference men ikke længere del af analyseflow.

### 2_total_use.ipynb
Sektorers andel af samlet energiforbrug pr. land over tid. Færdig.
- Subplot pr. sektor, linje pr. land
- Sektorrækkefølge: alfabetisk (matcher `2_electrification_rates.ipynb`)
- Sanity check: andele summer til ~100 % pr. land og år

### 3_decomposition.ipynb
Symmetrisk shift-share dekomponering. Færdig.
- **Analyse 1 (tidsserie)**: første → seneste observation pr. land, dekomponering i sammensætnings- og intensitetseffekt
- **Analyse 2 (tværsnit)**: DK vs. hvert andet land i seneste fælles år
- Beviscelle sidst: LaTeX-bevis for at C + I = ΔE eksakt med midtvejsvægte

### 4_greenpower.ipynb
Grøn energis andel af GIC og GEP over tid. To sektioner: Del 1 (GIC) og Del 2 (GEP).
- Inkluderede SIEC-koder: `RA100` (vandkraft), `RA300` (vind total), `RA420` (sol PV), `N900H` (kernekraft, termisk input), `R5110-5150_W6000RI` (fast biomasse + fornybart affald)
- `RA410` (sol termisk) er **ikke inkluderet** — producerer varme, ikke elektricitet, næsten nul produktion i EU
- On/offshore-split (`RA310`/`RA320`) returnerer HTTP 400 — ikke tilgængeligt på dette niveau
- Fig 1 (GIC): Grøn andel over tid, linje pr. land
- Fig 2 (GIC): Stablede søjler pr. land, kildebidrag for seneste år
- Fig 3 (GEP): Grøn andel af elproduktion over tid
- Fig 4 (GEP): Stablede søjler, kildebidrag seneste år

### 5_case_study.ipynb
Kontrafaktisk analyse: hvad sker der med EU's aggregerede elektrificeringsrate hvis `FC_TRA_ROAD_E` elektrificeres til 100%?
- `FC_TRA_ROAD_E` ("Vejtransport") dækker al vejtransport — lastbiler, personbiler, busser, motorcykler. Ingen yderligere disaggregering mulig i `nrg_bal_c`. Personbilers brændstof er i `FC_TRA_ROAD_E`, **ikke** i `FC_OTH_HH_E`.
- Disaggregering til lastbil vs. personbil kræver IEA Extended Energy Balances (betaling) eller ODYSSEE-MURE.
- Kontrafaktisk gevinst: $\Delta E_\text{agg} = s_\text{road} \cdot (1 - e_\text{road}/100)$
- Energivægt $s_\text{road}$ fra `df_enw.parquet` (total energi, SIEC=TOTAL) — **ikke** fra `fetch_elec_consumption`

### 0_old/1_fetch.ipynb
Backup af original fetch-notebook (med GVA) før overgang til energivægte.

## Shift-share — metodisk udgangspunkt

Elektrificeringsraten for land $c$ i år $t$:

$$E_{c,t} = \sum_i s_{i,c,t} \cdot e_{i,c,t}$$

hvor $s_{i,c,t}$ = sektor $i$'s andel af samlet energiforbrug (TJ) og $e_{i,c,t}$ = elektrificeringsrate i sektor $i$.

**Symmetrisk dekomponering med midtvejsvægte** (ingen interaktionsled — algebraisk identitet):

$$\Delta E = \underbrace{\sum_i \Delta s_i \cdot \bar{e}_i}_{\text{sammensætning}} + \underbrace{\sum_i \bar{s}_i \cdot \Delta e_i}_{\text{intensitet}}, \qquad \bar{s}_i = \tfrac{s_0+s_1}{2},\; \bar{e}_i = \tfrac{e_0+e_1}{2}$$

## Dataadgang
`df.parquet` kolonner: `geo`, `year`, `nrg_bal`, `label`, `elec_share_pct`, `energy_tj`

Relevante sektorer: `var_groups.subs` minus `_excl = {'FC_OTH_NSP_E', 'FC_TRA_NSP_E', 'FC_TRA_DAVI_E', 'FC_TRA_DNAVI_E'}`.
Brug `.fillna(0)` for manglende energidata.