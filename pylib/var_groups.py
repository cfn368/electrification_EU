

# ========== ========== ========== ========== ==========
# ========== 1. Structure of electrification data
countries = [
    'DK','SE',
    # 'NO',
    'DE','NL','FR',
    'FI',
    'EU27_2020',    # EU, 27 countries, 2020-
]

country_names = {
    'DK':        'Danmark',
    'SE':        'Sverige',
    # 'NO':        'Norge',
    'DE':        'Tyskland',
    'NL':        'Holland',
    # 'ES':        'Spanien',
    'FR':        'Frankrig',
    # 'UK':        'UK',
    'FI':        'Finland',
    'EU27_2020': 'EU-27 gns.',
}

total = ['FC_E']        # Final consumption 

parent = [
    'FC_IND_E',         # Industry sector   
    'FC_TRA_E',         # Transport sector  
    'FC_OTH_E',         # Other sectors
]

subs = [
    # Transport
    'FC_IND_IS_E',      # iron and steel
    'FC_IND_CPC_E',     # chemical and petrochemical
    'FC_IND_NFM_E',     # non-ferrous metals
    'FC_IND_NMM_E',     # non-metallic minerals
    'FC_IND_TE_E',      # transport equipment
    'FC_IND_MAC_E',     # machinery !!
    'FC_IND_MQ_E',      # mining and quarrying
    'FC_IND_FBT_E',     # food, beverages and tobacco
    'FC_IND_PPP_E',     # paper, pulp and printing
    'FC_IND_WP_E',      # wood and wood products
    'FC_IND_CON_E',     # construction
    'FC_IND_TL_E',      # textile and leather
    'FC_IND_NSP_E',     # not elsewhere specified

    # Transport
    'FC_TRA_RAIL_E',    # rail
    'FC_TRA_ROAD_E',    # road
    'FC_TRA_DAVI_E',    # domestic aviation
    'FC_TRA_DNAVI_E',   # domestic navigation
    'FC_TRA_PIPE_E',    # pipeline transport !!
    'FC_TRA_NSP_E',     # not elsewhere specified !!

    # Other
    'FC_OTH_CP_E',      # commercial and public services !!
    'FC_OTH_HH_E',      # households
    'FC_OTH_AF_E',      # agriculture and forestry
    'FC_OTH_FISH_E',    # fishing
    'FC_OTH_NSP_E',     # not elsewhere specified !!
]


labels = {
    'FC_E':         'Endeligt forbrug',
    'FC_IND_E':     'Industri',
    'FC_TRA_E':     'Transport',
    'FC_OTH_E':     'Øvrige sektorer',
    'FC_IND_IS_E':  'Jern og stål',
    'FC_IND_CPC_E': 'Kemi og petrokemi',
    'FC_IND_NFM_E': 'Ikke-jernholdige metaller',
    'FC_IND_NMM_E': 'Ikke-metalliske mineraler',
    'FC_IND_TE_E':  'Transportudstyr',
    'FC_IND_MAC_E': 'Maskiner og udstyr',
    'FC_IND_MQ_E':  'Minedrift og råstofudvinding',
    'FC_IND_FBT_E': 'Føde-, drikke- og tobaksvarer',
    'FC_IND_PPP_E': 'Papir, papirmasse og trykning',
    'FC_IND_WP_E':  'Træ og træprodukter',
    'FC_IND_CON_E': 'Byggeri og anlæg',
    'FC_IND_TL_E':  'Tekstil og læder',
    'FC_IND_NSP_E': 'Industri – ikke specificeret',
    'FC_TRA_RAIL_E':  'Jernbane',
    'FC_TRA_ROAD_E':  'Vejtransport',
    'FC_TRA_DAVI_E':  'Indenrigsluftfart',
    'FC_TRA_DNAVI_E': 'Indenrigssøfart',
    'FC_TRA_PIPE_E':  'Rørledninger',
    'FC_TRA_NSP_E':   'Transport – ikke specificeret',
    'FC_OTH_CP_E':   'Private og offentlige tjenester',
    'FC_OTH_HH_E':   'Husholdninger',
    'FC_OTH_AF_E':   'Landbrug og skovbrug',
    'FC_OTH_FISH_E': 'Fiskeri',
    'FC_OTH_NSP_E':  'Øvrige – ikke specificeret',
}


# ========== ========== ========== ========== ==========
# ========== 2. Grouping map to NACE64
nace_map = {
    # Industry — FC_IND
    'FC_IND_IS_E':  [],                            # C24 split equally with NFM in fetch_gva (inseparable in A64)
    'FC_IND_CPC_E': ['C20', 'C21'],               # chemicals + pharma
    'FC_IND_NFM_E': [],                           # C24 split equally with IS in fetch_gva (inseparable in A64)
    'FC_IND_NMM_E': ['C23'],                      # non-metallic minerals
    'FC_IND_TE_E':  ['C29_C30'],                  # transport equipment (motor vehicles + other)
    'FC_IND_MAC_E': ['C25', 'C26', 'C27', 'C28'], # fabricated metal, electronics, electrical, machinery
    'FC_IND_MQ_E':  ['B'],                        # mining & quarrying
    'FC_IND_FBT_E': ['C10-C12'],                  # food, beverages, tobacco
    'FC_IND_PPP_E': ['C17', 'C18'],               # paper + printing
    'FC_IND_WP_E':  ['C16'],                      # wood
    'FC_IND_CON_E': ['F'],                        # construction
    'FC_IND_TL_E':  ['C13-C15'],                  # textiles, apparel, leather
    'FC_IND_NSP_E': ['C22', 'C31_C32', 'C33'],    # rubber/plastics, furniture/other, repair

    # Other — FC_OTH
    'FC_OTH_CP_E':  [                              # commercial & public services
        'G', 'I',                                  # trade, accommodation
        'J',                                       # information & communication
        'K',                                       # financial
        'L',                                       # real estate (see note on L68A)
        'M', 'N',                                  # professional + admin services
        'O', 'P', 'Q',                             # public admin, education, health
        'R', 'S',                                  # arts, other services
        'U',                                       # extraterritorial
        'H52', 'H53',                              # warehousing + postal (H49/50/51 → transport below)
    ],
    # Transport — mapped in fetch_gva via equal H49 split; H50/H51 direct
    # FC_TRA_RAIL_E / FC_TRA_ROAD_E / FC_TRA_PIPE_E ← H49 / 3 each
    # FC_TRA_DNAVI_E ← H50
    # FC_TRA_DAVI_E  ← H51
    'FC_OTH_AF_E':  ['A01', 'A02'],               # agriculture + forestry
    'FC_OTH_FISH_E':['A03'],                      # fishing
    'FC_OTH_HH_E':  ['T'],                        # households as employers (proxy — see note)
    'FC_OTH_NSP_E': [],                           # residual — no clean NACE counterpart
}

# Reverse: nace_r2 code → nrg_bal sector
nace_to_nrg = {nace: nrg for nrg, naces in nace_map.items() for nace in naces}
# check how much of total NACE prod the above is catching.