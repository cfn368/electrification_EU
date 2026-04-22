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
| `df.parquet` | Kombineret datasæt: elektrificeringsrate + GVA (M EUR) pr. land, år og delsektor |

### Hentning
- `1_fetch.ipynb` henter data fra Eurostat via `pylib/fetches.py`
- Elektricitetsforbrug: NRG_BAL_C (Eurostat energy balances)
- GVA: NAMA_10_A64 (Eurostat nationalregnskab, A64-klassifikation)
- GVA er mappet fra NACE-koder til energisektorer via `var_groups.nace_map`

### Lande
`var_groups.countries`: DK, SE, NO, DE, NL, ES, FR, UK, FI, EU27_2020

EU27_2020-værdier divideres med 27 for at give et per-land gennemsnit i alle figurer.

## Kodestruktur

### pylib/
| Fil | Indhold |
|-----|---------|
| `preamble.py` | Standardimports (pandas, numpy, matplotlib, var_groups m.m.) |
| `fig_setup.py` | Figuropsætning: `PALETTE`, `STYLE`, `LW`, `SEC_PALETTE`, `style_ax()`, `country_handles()` |
| `var_groups.py` | Metadata: landekoder, sektorkoder, `labels` (dansk), `country_names`, `nace_map` |
| `fetches.py` | Datafetching fra Eurostat |

### Vigtige konventioner
- `style_ax(ax, years, step=5)` — sætter grid, xlim og x-tick-interval (brug `step=10` for tætte figurer)
- `country_handles(countries)` — returnerer legend-handles med fulde landenavne fra `var_groups.country_names`
- `SEC_PALETTE` — 20-farve palette til sektorfigurer (de første 10 er projektets standardfarver)
- Stablede søjlediagrammer: brug **altid** integer x-positioner (`np.arange`) + `.to_numpy()` + `.fillna(0)` — pandas categorical axis i matplotlib giver stille fejl

## Notebooks

### 2_electrification_rates.ipynb
Deskriptiv analyse af elektrificeringsrater. Færdig.
- Fig 1–4: aggregeret rate og overordnede sektorer (absolutt + indekseret)
- Fig 5: DK vs. EU27 på delsektorniveau, 4 kolonner, legend nedenunder

### 2_GVA.ipynb
GVA-datakvalitetskontrol. Færdig.
- Fig 1: GVA-tidsserie pr. sektor, alle lande, 4 kolonner
- Fig 2: Stablede søjler pr. land, GVA-sammensætning 2015 (med og uden handel/offentlige tjenester)

### 3_decomposition.ipynb
**Ikke påbegyndt — dette er næste skridt.**
Skal indeholde selve shift-share-dekomponeringen.

## Shift-share — metodisk udgangspunkt

Elektrificeringsraten for land $c$ i år $t$:

$$E_{c,t} = \sum_i s_{i,c,t} \cdot e_{i,c,t}$$

hvor $s_{i,c,t}$ = sektor $i$'s GVA-andel og $e_{i,c,t}$ = elektrificeringsrate i sektor $i$.

Ændringen $\Delta E_{c}$ kan dekomponeres i:
- **Composition effect**: ændring i $s$ (erhvervsstruktur), holdt $e$ fast
- **Intensity effect**: ændring i $e$ (sektorspecifik elektrificering), holdt $s$ fast
- **Interaction term**: samspil mellem de to

Sammenligningen sker typisk enten over tid (samme land, to år) eller på tværs af lande
(DK vs. EU27-gennemsnit i samme år).

## Dataadgang
`df.parquet` har kolonnerne: `geo`, `year`, `nrg_bal`, `label`, `elec_share_pct`, `gva_meur`

Relevante sektorer til dekomponeringen er `var_groups.subs` (delsektorer) — undtagen dem
der mangler GVA-mapping (`FC_IND_IS_E`, `FC_IND_NFM_E`, `FC_TRA_*` med tomme nace_map-lister,
`FC_OTH_NSP_E`). GVA for visse lande/sektorer er NaN — brug `.fillna(0)` efter pivot.
