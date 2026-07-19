# Configuració del mapa de Barcelona (AMB ampliada)
# Edita aquest fitxer per ajustar l'àrea, la demanda i els punts especials.

CITY_CODE = "BCN"
MAP_NAME = "Barcelona (regió metropolitana)"
MAP_DESCRIPTION = ("Regió metropolitana de Barcelona: de Coma-ruga a Maçanet de "
                   "la Selva, amb Manresa i Igualada. Demanda censal 2021.")
CREATOR = "David"  # el teu nom/usuari
VERSION = "1.1.0"
COUNTRY = "ES"

# [min_lon, min_lat, max_lon, max_lat]
# Cobreix de Coma-ruga (el Vendrell) fins a Maçanet de la Selva/Blanes,
# i cap a l'interior fins a Igualada i Manresa.
BBOX = [1.45, 41.14, 2.82, 41.82]

INITIAL_VIEW = [2.1688, 41.3887]  # Pl. Catalunya

# --- Mapa base (etiquetes) ---
LABEL_CITIES = ["city", "town"]
LABEL_SUBURBS = ["town", "suburb", "village"]
LABEL_NEIGHBORHOODS = ["suburb", "neighbourhood", "quarter"]
LABEL_LANGUAGE = "prefer:ca"       # etiquetes en català si existeixen
ROAD_NAME_LANGUAGE = "ca"

# --- Model de demanda ---
SUBCELL_M = 500          # resolució de subcel·la (m); la graella font és d'1 km
BETA_KM = 5.0            # paràmetre de decaïment del model gravitatori
MAX_COMMUTE_KM = 45.0    # distància màxima de desplaçament considerada
COMMUTE_SHARE = 0.85     # fracció d'ocupats que es desplacen un dia laborable
POP_SIZE = 200           # mida màxima de població per grup (recomanat pel joc)
MIN_POINT_ACTIVITY = 25  # descarta subcel·les amb menys activitat total
MAX_ROUTE_WORKERS = 4    # paral·lelisme del càlcul de rutes (RAM!)

# Pes relatiu de cada m2 per assignar llocs de treball (proxy OSM)
JOB_WEIGHTS = {
    "office": 3.0,
    "retail": 2.0,
    "commercial": 1.5,
    "industrial": 0.6,
    "civic": 1.5,       # equipaments
    "other_building": 0.15,
}

# --- Demanda especial ---
# Cada entrada: (codi, tipus, nom, [lon, lat], capacitat diària, pop_size,
#                merge_within_m, max_distance_m o None, residential_split o None)
SPECIAL_POINTS = [
    # Aeroport i port
    ("BCN1", "airport", "Aeroport de Barcelona T1", [2.0745, 41.2872], 105000, 200, 350, None, None),
    ("BCN2", "airport", "Aeroport de Barcelona T2", [2.0996, 41.2975], 45000, 200, 300, None, None),
    ("PORT", "port", "Port de Barcelona (creuers)", [2.1770, 41.3705], 25000, 100, 300, None, None),
    # Universitats (estudiants; residential_split = % que viu al campus)
    ("UBDG", "university", "UB/UPC Zona Universitària", [2.1140, 41.3860], 45000, 200, 400, 30000, 0.05),
    ("UBHV", "university", "UB Campus Històric (Raval)", [2.1640, 41.3867], 18000, 200, 300, 25000, 0.0),
    ("UPF1", "university", "UPF Ciutadella", [2.1846, 41.3908], 12000, 100, 250, 25000, 0.0),
    ("UAB1", "university", "UAB Bellaterra", [2.1040, 41.5010], 35000, 200, 500, 45000, 0.15),
    ("UBMN", "university", "UB Campus Mundet", [2.1447, 41.4400], 8000, 100, 250, 25000, 0.0),
    # Hospitals
    ("HVHB", "hospital", "Hospital Vall d'Hebron", [2.1420, 41.4260], 12000, 100, 300, None, None),
    ("HCLI", "hospital", "Hospital Clínic", [2.1510, 41.3890], 9000, 100, 250, None, None),
    ("HSPU", "hospital", "Hospital de Sant Pau", [2.1740, 41.4130], 8000, 100, 250, None, None),
    ("HBLV", "hospital", "Hospital de Bellvitge", [2.1000, 41.3460], 8000, 100, 250, None, None),
    ("HGTP", "hospital", "Germans Trias (Can Ruti)", [2.2400, 41.4640], 6000, 100, 250, None, None),
    ("HPTS", "hospital", "Parc Taulí (Sabadell)", [2.1080, 41.5560], 6000, 100, 250, None, None),
    ("HMTR", "hospital", "Mútua de Terrassa", [2.0110, 41.5630], 5000, 100, 250, None, None),
    ("HMAT", "hospital", "Hospital de Mataró", [2.4270, 41.5480], 4000, 50, 250, None, None),
    # Esport i grans esdeveniments
    ("CAMP", "sports_facility", "Spotify Camp Nou", [2.1228, 41.3809], 15000, 200, 400, 40000, None),
    ("MJUI", "events", "Anella Olímpica (Montjuïc)", [2.1526, 41.3644], 8000, 200, 400, 35000, None),
    ("RCDE", "sports_facility", "RCDE Stadium (Cornellà)", [2.0759, 41.3475], 6000, 200, 300, 35000, None),
    # Turisme i lleure
    ("SGFM", "heritage_site", "Sagrada Família", [2.1744, 41.4036], 12000, 100, 250, None, None),
    ("PKGU", "park", "Park Güell", [2.1527, 41.4145], 8000, 100, 300, None, None),
    ("TBDB", "amusement_park", "Tibidabo", [2.1187, 41.4225], 4000, 50, 300, 30000, None),
    ("BCTA", "natural_feature", "Platja de la Barceloneta", [2.1968, 41.3785], 15000, 100, 400, 25000, None),
    ("CSTD", "natural_feature", "Platges de Castelldefels", [1.9800, 41.2680], 8000, 100, 500, 30000, None),
    ("ZOOB", "zoo", "Zoo de Barcelona", [2.1900, 41.3860], 3000, 50, 250, 25000, None),
    ("MNAC", "museum", "MNAC (Montjuïc)", [2.1534, 41.3684], 4000, 50, 250, None, None),
    # Fires i convencions
    ("FGRV", "convention_center", "Fira Gran Via", [2.1290, 41.3540], 10000, 200, 400, None, None),
    ("FMJC", "convention_center", "Fira Montjuïc", [2.1497, 41.3720], 6000, 100, 300, None, None),
    # Centres comercials
    ("MAQN", "shopping_center", "La Maquinista", [2.1983, 41.4395], 25000, 200, 350, 20000, None),
    ("GLRS", "shopping_center", "Westfield Glòries", [2.1927, 41.4056], 20000, 200, 300, 15000, None),
    ("SPLU", "shopping_center", "Splau (Cornellà)", [2.0810, 41.3450], 18000, 200, 300, 20000, None),
    ("DGMR", "shopping_center", "Diagonal Mar", [2.2163, 41.4100], 18000, 200, 300, 15000, None),
    ("ILLA", "shopping_center", "L'Illa Diagonal", [2.1360, 41.3888], 12000, 200, 250, 15000, None),
    ("MTPC", "shopping_center", "Mataró Parc", [2.4230, 41.5560], 12000, 200, 300, 25000, None),
    # Zones noves (coordenades aproximades — ajusta-les si cal)
    ("HALT", "hospital", "Althaia (Manresa)", [1.8190, 41.7300], 5000, 100, 250, None, None),
    ("HIGD", "hospital", "Hospital d'Igualada", [1.6320, 41.5760], 3500, 50, 250, None, None),
    ("HBLN", "hospital", "Hospital de Blanes", [2.7790, 41.6870], 3000, 50, 250, None, None),
    ("HVNG", "hospital", "Sant Camil (Garraf)", [1.7710, 41.2440], 3500, 50, 250, None, None),
    ("CMRG", "natural_feature", "Platja de Coma-ruga", [1.5180, 41.1720], 6000, 100, 500, 35000, None),
    ("SITG", "natural_feature", "Platges de Sitges", [1.8130, 41.2340], 8000, 100, 400, 30000, None),
    ("BLNS", "natural_feature", "Platja de Blanes", [2.7920, 41.6720], 6000, 100, 400, 30000, None),
    ("UMAN", "university", "UManresa/UPC Manresa", [1.8280, 41.7370], 4000, 50, 250, 30000, 0.0),
]
