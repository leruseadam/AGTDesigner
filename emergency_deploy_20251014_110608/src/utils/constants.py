from typing import Dict

LINEAGE_COLOR_MAP: Dict[str, str] = {
    "HYBRID/SATIVA": "#ED4123",
    "HYBRID/INDICA": "#9900FF",
    "SATIVA": "#ED4123",
    "INDICA": "#9900FF",
    "HYBRID": "#009900",
    "CBD": "#F1C232",
    "MIXED": "#0021F5",
    "PARAPHERNALIA": "#FFC0CB",
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