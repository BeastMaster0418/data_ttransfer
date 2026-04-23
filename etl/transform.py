import pandas as pd
from config import OUTPUT_COLUMNS
from utils.helpers import (
    clean_text,
    safe_ref,
    incidental_flag,
    semi_colon_join,
    clamp_0_100,
    limit_decimals,
)
from utils.parsers import (
    parse_inci_comp,
    extract_number_max,
    extract_impurity_unit,
    extract_allergen_max,
)


# ── Customer lookup ──────────────────────────────────────────────────────────

def _build_customer_lookup(customer: pd.DataFrame) -> pd.DataFrame:
    """
    Index customer data by the numeric suffix of Item ID.
    e.g. 'GFP-10001' -> key 10001.0
    """
    df = customer.copy()
    df["_key"] = df["Item ID"].astype(str).str.extract(r"(\d+)$")[0]
    df["_key"] = pd.to_numeric(df["_key"], errors="coerce")
    return df.dropna(subset=["_key"]).set_index("_key")


def _get_customer_field(lookup: pd.DataFrame, ref_num, field: str):
    """Look up a single field from the customer table by reference number."""
    try:
        key = float(ref_num)
    except (TypeError, ValueError):
        return None
    if key not in lookup.index:
        return None
    row = lookup.loc[key]
    val = row[field] if isinstance(row, pd.Series) else row[field].iloc[0]
    return str(val).strip() if pd.notna(val) else None


# ── Row builder ──────────────────────────────────────────────────────────────

def _build_row(src_row: pd.Series, lookup: pd.DataFrame, is_first: bool) -> dict:
    """Map one Extraction File row to one output template row."""
    ref     = src_row["Reference Number"]
    ref_str = safe_ref(ref)

    inci_exact, inci_min, inci_max = parse_inci_comp(src_row.get("INCI Comp"))

    imp_raw  = src_row.get("Impurity Comp")
    imp_num  = extract_number_max(imp_raw)
    imp_unit = extract_impurity_unit(imp_raw) if pd.notna(imp_raw) else None

    alg_num  = extract_allergen_max(src_row.get("Allergen Comp"))

    trade_name = (
        (
            _get_customer_field(lookup, ref, "Client Preferred Trade Name")
            or clean_text(src_row.get("Trade Name"), 255)
        )
        if is_first
        else None
    )

    return {
        "Trade Name":                             trade_name,
        "Manufacturer":                           clean_text(src_row.get("Manufacturer"), 255),
        "Supplier&Distributor":                   ref_str,
        "Reference Number":                       ref_str if is_first else None,
        "INCI Name":                              clean_text(src_row.get("INCI"), 200),
        "CAS INCI / Incidental":                  ref_str,
        "Is Incidental?":                         incidental_flag(src_row.get("Incidental?")),
        "INCI Concentration":                     clamp_0_100(inci_exact),
        "INCI Conc Min":                          clamp_0_100(inci_min),
        "INCI Conc Max":                          clamp_0_100(inci_max),
        "INCI Function":                          semi_colon_join(src_row.get("Function"), 255),
        "Impurity Name":                          clean_text(src_row.get("Impurity"), 200),
        "CAS Impurity":                           ref_str,
        "Impurity Concentration":                 limit_decimals(imp_num),
        "Impurity Concentration type (% or PPM)": imp_unit,
        "Allergen Name":                          clean_text(src_row.get("Allergens"), 200),
        "CAS Allergen":                           ref_str,
        "Allergen Concentration":                 clamp_0_100(alg_num),
        "RM Status":                              _get_customer_field(lookup, ref, "Status"),
        "Is Locked":                              "No",
        "Price":                                  None,
        "Price: From":                            None,
        "Price: To":                              None,
        "Description":                            None,
    }


# ── Public entry point ───────────────────────────────────────────────────────

def transform(extraction: pd.DataFrame, customer: pd.DataFrame) -> pd.DataFrame:
    """
    Full transformation pipeline:
      1. Forward-fill Reference Number (sub-rows inherit parent ref)
      2. Build customer lookup index
      3. Map every row to the output template schema
      4. Deduplicate Trade Name / Reference Number within each group

    Returns a DataFrame with OUTPUT_COLUMNS column order.
    """
    # Step 1 – forward-fill reference numbers
    extraction = extraction.copy()
    extraction["Reference Number"] = extraction["Reference Number"].ffill()

    # Step 2 – customer lookup
    lookup = _build_customer_lookup(customer)

    # Step 3 – build rows
    rows      = []
    last_ref  = None

    for _, row in extraction.iterrows():
        ref_str  = safe_ref(row["Reference Number"])
        is_first = ref_str != last_ref
        last_ref = ref_str
        rows.append(_build_row(row, lookup, is_first))

    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
