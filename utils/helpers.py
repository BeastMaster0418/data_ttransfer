import re
import math
import pandas as pd

NUMBER_RE = re.compile(r'\d+\.?\d*(?:[eE][+-]?\d+)?')


def safe_float(s):
    try:
        v = float(s)
        return v if math.isfinite(v) else None
    except (ValueError, TypeError):
        return None


def clean_text(val, max_len=None):
    """Strip whitespace and optionally truncate."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    result = str(val).strip()
    return result[:max_len] if max_len else result


def safe_ref(val):
    """Convert float reference numbers like 10001.0 -> '10001', truncate to 30 chars."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    try:
        result = str(int(float(val)))
    except (TypeError, ValueError):
        result = str(val).strip()
    return result[:30]


def incidental_flag(val):
    """Normalise Y/YES/1/TRUE -> 'Yes', anything else -> 'No'."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "No"
    return "Yes" if str(val).strip().upper() in ("Y", "YES", "1", "TRUE") else "No"


def semi_colon_join(val, max_len=255):
    """Split on commas/semicolons and rejoin as '; '-separated string."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    parts = re.split(r"[;,]", str(val))
    result = "; ".join(p.strip() for p in parts if p.strip())
    return result[:max_len]


def clamp_0_100(val):
    """Return value only if within [0, 100], else None."""
    if val is None:
        return None
    return round(val, 8) if 0 <= val <= 100 else None


def limit_decimals(val, decimals=8):
    """Round to given decimal places."""
    if val is None:
        return None
    return round(val, decimals)
