import pandas as pd
import re
import math
from decimal import Decimal, InvalidOperation, ROUND_DOWN

# ── Load source files ────────────────────────────────────────────────────────
a_df = pd.read_excel('data/Extraction File.xlsx')
b_df = pd.read_excel('data/Customer Supplied RM List.xlsx')

# ── Build B lookup: numeric part of Item ID -> row ──────────────────────────
b_df['_key'] = b_df['Item ID'].astype(str).str.extract(r'(\d+)$')[0]
b_df['_key'] = pd.to_numeric(b_df['_key'], errors='coerce')
b_lookup = b_df.dropna(subset=['_key']).set_index('_key')

# ── Forward-fill Reference Number within A ──────────────────────────────────
a_df['Reference Number'] = a_df['Reference Number'].ffill()

# ── Helper functions ─────────────────────────────────────────────────────────

NUMBER_RE = re.compile(r'\d+\.?\d*(?:[eE][+-]?\d+)?')

def safe_float(s):
    try:
        v = float(s)
        return v if math.isfinite(v) else None
    except (ValueError, TypeError):
        return None

def extract_number_max(val):
    """Extract the maximum numeric value from messy strings."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    s = str(val).strip()
    # Remove leading operators / keywords
    s = re.sub(r'(?i)^(max\.?|nmt|<=?|>=?|~|˂|≤|≥|≦|≧)\s*', '', s).strip()
    # Remove trailing keywords
    s = re.sub(r'(?i)\s*(ppm|ppb|mg/kg|μg/kg|ug/kg|mg/l|%)\s*(max\.?|max)?\s*$', '', s).strip()
    s = re.sub(r'(?i)\s*max\.?\s*$', '', s).strip()
    # Range → take max
    m = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', s)
    if m:
        v = safe_float(m.group(2))
        return round(v, 8) if v is not None else None
    # Single number
    nums = NUMBER_RE.findall(s)
    for n in nums:
        v = safe_float(n)
        if v is not None:
            return round(v, 8)
    return None

def extract_impurity_unit(val):
    """Return 'PPM' if ppm/ppb/mg/kg present, else '%'."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    s = str(val).upper()
    if re.search(r'PPM|PPB|MG/KG|[UΜ]G/KG|MG/L', s):
        return 'PPM'
    return '%'

def parse_inci_comp(val):
    """Return (exact, min, max) rounded to 8 decimals."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None, None, None
    s = str(val).strip()
    # Range
    m = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', s)
    if m:
        lo = safe_float(m.group(1))
        hi = safe_float(m.group(2))
        return None, (round(lo, 8) if lo is not None else None), (round(hi, 8) if hi is not None else None)
    # Inequality
    m2 = re.match(r'([<>≤≥]=?)\s*(\d+\.?\d*)', s)
    if m2:
        num = safe_float(m2.group(2))
        num = round(num, 8) if num is not None else None
        op = m2.group(1)
        if '<' in op or '≤' in op:
            return None, None, num
        else:
            return None, num, None
    # Plain number
    nums = NUMBER_RE.findall(s)
    for n in nums:
        v = safe_float(n)
        if v is not None:
            return round(v, 8), None, None
    return None, None, None

def extract_allergen_max(val):
    """Extract allergen concentration (0-100), taking max of range."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    s = str(val).strip()
    # Strip known non-numeric units that disqualify value
    if re.search(r'(?i)μg/kg|ug/kg|mg/kg|mg/l', s):
        return None  # unit not compatible with 0-100 %
    s = re.sub(r'(?i)(MAX\.?|<=?|>=?|~|˂|≤|≥|<|>)\s*', '', s).strip()
    # Range
    m = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', s)
    if m:
        v = safe_float(m.group(2))
        return round(v, 8) if v is not None else None
    nums = NUMBER_RE.findall(s)
    for n in nums:
        v = safe_float(n)
        if v is not None:
            return round(v, 8)
    return None

def clean_text(val, max_len):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    return str(val).strip()[:max_len]

def incidental_flag(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return ''
    return 'Y' if str(val).strip().upper() in ('Y', 'YES', '1', 'TRUE') else 'No'

def get_b_field(ref_num, field):
    try:
        key = float(ref_num)
    except (TypeError, ValueError):
        return None
    if key not in b_lookup.index:
        return None
    row = b_lookup.loc[key]
    val = row[field] if isinstance(row, pd.Series) else row[field].iloc[0]
    return str(val).strip() if pd.notna(val) else None

def semi_colon_join(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    parts = re.split(r'[;,]', str(val))
    result = '; '.join(p.strip() for p in parts if p.strip())
    return result[:255]

def safe_ref(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    try:
        return str(int(float(val)))
    except (TypeError, ValueError):
        return str(val).strip()
    
def clean_numeric(value, min_val=None, max_val=None, max_decimals=8):
    if value is None or value == '':
        return None
    try:
        num = Decimal(str(value))
    except InvalidOperation:
        return None

    # Apply range limits
    if min_val is not None and num < Decimal(str(min_val)):
        return None
    if max_val is not None and num > Decimal(str(max_val)):
        return None

    # Limit decimal places (truncate, not round up)
    quantize_str = '1.' + '0' * max_decimals
    num = num.quantize(Decimal(quantize_str), rounding=ROUND_DOWN)

    return float(num)

def get_null():
    return None

# ── Build output rows ────────────────────────────────────────────────────────
C_COLS = [
    'Trade Name', 'Manufacturer', 'Supplier&Distributor', 'Reference Number',
    'INCI Name', 'CAS INCI / Incidental', 'Is Incidental?', 'INCI Concentration',
    'INCI Conc Min', 'INCI Conc Max', 'INCI Function', 'Impurity Name',
    'CAS Impurity', 'Impurity Concentration', 'Impurity Concentration type (% or PPM)',
    'Allergen Name', 'CAS Allergen', 'Allergen Concentration', 'RM Status',
    'Is Locked', 'Price', 'Price: From', 'Price: To', 'Description'
]

rows = []
last_ref = None
for _, row in a_df.iterrows():
    ref      = row['Reference Number']
    ref_str  = safe_ref(ref)

    inci_exact, inci_min, inci_max = parse_inci_comp(row.get('INCI Comp'))

    imp_raw  = row.get('Impurity Comp')
    imp_num  = extract_number_max(imp_raw)
    imp_unit = extract_impurity_unit(imp_raw) if pd.notna(imp_raw) else None

    alg_num  = extract_allergen_max(row.get('Allergen Comp'))
    
    is_first = (ref_str != last_ref)
    last_ref = ref_str

    rows.append({
        'Trade Name':                             (clean_text(get_b_field(ref, 'Client Preferred Trade Name'), 220) or clean_text(row.get('Trade Name'), 220)) if is_first else None,
        'Manufacturer':                           clean_text(row.get('Manufacturer'), 100),
        'Supplier&Distributor':                   None,
        'Reference Number':                       clean_text(ref_str if is_first else None, 30),
        'INCI Name':                              clean_text(row.get('INCI'), 200),
        'CAS INCI / Incidental':                  None,
        'Is Incidental?':                         incidental_flag(row.get('Incidental?')),
        'INCI Concentration':                     clean_numeric(inci_exact, 0, 100, 8),
        'INCI Conc Min':                          clean_numeric(inci_min, 0, 100, 8),
        'INCI Conc Max':                          clean_numeric(inci_max, 0, 100, 8),
        'INCI Function':                          semi_colon_join(row.get('Function')),
        'Impurity Name':                          clean_text(row.get('Impurity'), 200),
        'CAS Impurity':                           None,
        'Impurity Concentration':                 clean_numeric(imp_num, None, None, 8),
        'Impurity Concentration type (% or PPM)': imp_unit,
        'Allergen Name':                          clean_text(row.get('Allergens'), 200),
        'CAS Allergen':                           None,
        'Allergen Concentration':                 clean_numeric(alg_num, 0, 100, 8),
        'RM Status':                              get_b_field(ref, 'Status'),
        'Is Locked':                              'N',
        'Price':                                  None,
        'Price: From':                            None,
        'Price: To':                              None,
        'Description':                            clean_text(get_b_field(ref, 'Additional Description'), 2000),
    })

out_df = pd.DataFrame(rows, columns=C_COLS)
print(f"Output rows: {len(out_df)}")
print(out_df.head(15).to_string())

out_df.to_excel('Raw Materials Template (Hiring).xlsx', index=False)
print("\nSaved successfully.")
