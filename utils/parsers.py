import re
import math
import pandas as pd
from utils.helpers import safe_float, NUMBER_RE


def extract_number_max(val):
    """
    Extract the maximum numeric value from messy concentration strings.
    Handles: '< 3 ppm', 'max 1 ppm', '4 - 6', '51 - 59', numeric literals, etc.
    For ranges, returns the upper bound.
    """
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    s = str(val).strip()

    # Remove leading operators / keywords
    s = re.sub(r"(?i)^(max\.?|nmt|<=?|>=?|~|˂|≤|≥|≦|≧)\s*", "", s).strip()
    # Remove trailing units (with optional trailing 'max')
    s = re.sub(r"(?i)\s*(ppm|ppb|mg/kg|μg/kg|ug/kg|mg/l|%)\s*(max\.?)?\s*$", "", s).strip()
    s = re.sub(r"(?i)\s*max\.?\s*$", "", s).strip()

    # Range → take upper bound
    m = re.search(r"(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)", s)
    if m:
        v = safe_float(m.group(2))
        return round(v, 8) if v is not None else None

    # Single number
    for n in NUMBER_RE.findall(s):
        v = safe_float(n)
        if v is not None:
            return round(v, 8)
    return None


def extract_impurity_unit(val):
    """
    Classify impurity concentration unit.
    Returns 'PPM' if ppm / ppb / mg/kg / μg/kg / mg/L detected, else '%'.
    """
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    s = str(val).upper()
    if re.search(r"PPM|PPB|MG/KG|[UΜ]G/KG|MG/L", s):
        return "PPM"
    return "%"


def parse_inci_comp(val):
    """
    Parse INCI composition into (exact, min, max).
    - 'X - Y'   -> (None, X, Y)
    - '< X'     -> (None, None, X)
    - '> X'     -> (None, X, None)
    - 'X'       -> (X,    None, None)
    All values rounded to 8 decimal places.
    """
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None, None, None
    s = str(val).strip()

    # Range
    m = re.search(r"(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)", s)
    if m:
        lo = safe_float(m.group(1))
        hi = safe_float(m.group(2))
        return (
            None,
            round(lo, 8) if lo is not None else None,
            round(hi, 8) if hi is not None else None,
        )

    # Inequality
    m2 = re.match(r"([<>≤≥]=?)\s*(\d+\.?\d*)", s)
    if m2:
        num = safe_float(m2.group(2))
        num = round(num, 8) if num is not None else None
        op = m2.group(1)
        if "<" in op or "≤" in op:
            return None, None, num
        return None, num, None

    # Plain number
    for n in NUMBER_RE.findall(s):
        v = safe_float(n)
        if v is not None:
            return round(v, 8), None, None
    return None, None, None


def extract_allergen_max(val):
    """
    Extract allergen concentration (0–100 %), taking the upper bound of ranges.
    Returns None for values expressed in incompatible units (μg/kg, mg/kg, mg/L).
    """
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    s = str(val).strip()

    # Incompatible units → skip
    if re.search(r"(?i)μg/kg|ug/kg|mg/kg|mg/l", s):
        return None

    s = re.sub(r"(?i)(MAX\.?|<=?|>=?|~|˂|≤|≥|<|>)\s*", "", s).strip()

    # Range → upper bound
    m = re.search(r"(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)", s)
    if m:
        v = safe_float(m.group(2))
        return round(v, 8) if v is not None else None

    for n in NUMBER_RE.findall(s):
        v = safe_float(n)
        if v is not None:
            return round(v, 8)
    return None
