from typing import Dict

LINEAGE_COLOR_MAP: Dict[str, str] = {
    "SATIVA": "#ED4123",        # rgba(237, 65, 35, 1.0) - matches --lineage-sativa
    "INDICA": "#A084E8",        # rgba(160, 132, 232, 1.0) - matches --lineage-indica  
    "HYBRID": "#7C3AED",        # rgba(124, 58, 237, 1.0) - matches --lineage-hybrid
    "HYBRID/SATIVA": "#ED4123", # rgba(237, 65, 35, 1.0) - matches --lineage-hybrid-sativa
    "HYBRID/INDICA": "#A084E8", # rgba(160, 132, 232, 1.0) - matches --lineage-hybrid-indica
    "CBD": "#F1C232",           # rgba(241, 194, 50, 1.0) - matches --lineage-cbd
    "MIXED": "#0021F5",         # rgba(0, 33, 245, 1.0) - matches --lineage-mixed
    "PARAPHERNALIA": "#FFC0CB", # rgba(255, 192, 203, 1.0) - matches --lineage-para
}

TYPE_OVERRIDES: Dict[str, str] = {
    "all-in-one": "vape cartridge",
    "rosin": "concentrate",
    "mini buds": "flower",
    "bud": "flower",
    "pre-roll": "Pre-roll",
    "alcohol/ethanol extract": "rso/co2 tankers",
    "Alcohol/Ethanol Extract": "rso/co2 tankers",
    "alcohol ethanol extract": "rso/co2 tankers",
    "Alcohol Ethanol Extract": "rso/co2 tankers",
    "c02/ethanol extract": "rso/co2 tankers",
    "CO2 Concentrate": "rso/co2 tankers",
    "co2 concentrate": "rso/co2 tankers",
}

WORD_WEIGHT = 5
SCALE_FACTOR = 1.0