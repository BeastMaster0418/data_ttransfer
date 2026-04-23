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

def build_customer_lookup_index(customer: pd.DataFrame) -> pd.DataFrame:
    """
    Index customer data by the numeric suffix of Item ID.
    e.g. 'GFP-10001' -> key 10001.0
    """
    df = customer.copy()
    df["_key"] = df["Item ID"].astype(str).str.extract(r"(\d+)$")[0]
    df["_key"] = pd.to_numeric(df["_key"], errors="coerce")
    return df.dropna(subset=["_key"]).set_index("_key")


def get_customer_field_by_ref(lookup: pd.DataFrame, ref_num, field: str):
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

def map_extraction_row_to_output(src_row: pd.Series, lookup: pd.DataFrame, is_first: bool) -> dict:
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
            get_customer_field_by_ref(lookup, ref, "Client Preferred Trade Name")
            or clean_text(src_row.get("Trade Name"), 255)
        )
        if is_first
        else None
    )

    manufacturer = clean_text(src_row.get("Manufacturer"), 255)
    supplier_distributer = None
    reference_number = ref_str if is_first else None
    inci_name = clean_text(src_row.get("INCI"), 200)
    cas_inci_incidental = None
    is_incidental = incidental_flag(src_row.get("Incidental?"))
    inci_concentration = clamp_0_100(inci_exact)
    inci_conc_min = clamp_0_100(inci_min)
    inci_conc_max = clamp_0_100(inci_max)
    inci_function = semi_colon_join(src_row.get("Function"), 255)
    impurity_name = clean_text(src_row.get("Impurity"), 200)
    cas_impurity = None
    impurity_concentration = limit_decimals(imp_num)
    impurity_concentration_type = imp_unit
    allergen_name = clean_text(src_row.get("Allergens"), 200)
    cas_allergen = None
    allergen_concentration = clamp_0_100(alg_num)
    rm_status = get_customer_field_by_ref(lookup, ref, "Status")
    is_locked = "No"
    price = None
    price_from = None
    price_to = None
    description = clean_text(get_customer_field_by_ref(lookup, ref, "Additional Description"), 2000)


    return {
        "Trade Name":                             trade_name,
        "Manufacturer":                           manufacturer,
        "Supplier&Distributor":                   supplier_distributer,
        "Reference Number":                       reference_number,
        "INCI Name":                              inci_name,
        "CAS INCI / Incidental":                  cas_inci_incidental,
        "Is Incidental?":                         is_incidental,
        "INCI Concentration":                     inci_concentration,
        "INCI Conc Min":                          inci_conc_min,
        "INCI Conc Max":                          inci_conc_max,
        "INCI Function":                          inci_function,
        "Impurity Name":                          impurity_name,
        "CAS Impurity":                           cas_impurity,
        "Impurity Concentration":                 impurity_concentration,
        "Impurity Concentration type (% or PPM)": impurity_concentration_type,
        "Allergen Name":                          allergen_name,
        "CAS Allergen":                           cas_allergen,
        "Allergen Concentration":                 allergen_concentration,
        "RM Status":                              rm_status,
        "Is Locked":                              is_locked,
        "Price":                                  price,
        "Price: From":                            price_from,
        "Price: To":                              price_to,
        "Description":                            description,
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
    lookup = build_customer_lookup_index(customer)

    # Step 3 – build rows
    rows      = []
    last_ref  = None

    for _, row in extraction.iterrows():
        ref_str  = safe_ref(row["Reference Number"])
        is_first = ref_str != last_ref
        last_ref = ref_str
        rows.append(map_extraction_row_to_output(row, lookup, is_first))

    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
