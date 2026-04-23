from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent
RAW_DIR         = BASE_DIR / "data" / "raw"
PROCESSED_DIR   = BASE_DIR / "data" / "processed"

EXTRACTION_FILE = RAW_DIR / "Extraction File.xlsx"
CUSTOMER_FILE   = RAW_DIR / "Customer Supplied RM List.xlsx"
OUTPUT_FILE     = PROCESSED_DIR / "Raw Materials Template(Hiring).xlsx"

# ── Output column order ──────────────────────────────────────────────────────
OUTPUT_COLUMNS = [
    "Trade Name",
    "Manufacturer",
    "Supplier&Distributor",
    "Reference Number",
    "INCI Name",
    "CAS INCI / Incidental",
    "Is Incidental?",
    "INCI Concentration",
    "INCI Conc Min",
    "INCI Conc Max",
    "INCI Function",
    "Impurity Name",
    "CAS Impurity",
    "Impurity Concentration",
    "Impurity Concentration type (% or PPM)",
    "Allergen Name",
    "CAS Allergen",
    "Allergen Concentration",
    "RM Status",
    "Is Locked",
    "Price",
    "Price: From",
    "Price: To",
    "Description",
]

# ── Field constraints ────────────────────────────────────────────────────────
CONSTRAINTS = {
    "Reference Number":          {"max_chars": 30},
    "INCI Concentration":        {"min": 0, "max": 100, "decimals": 8},
    "INCI Conc Min":             {"min": 0, "max": 100, "decimals": 8},
    "INCI Conc Max":             {"min": 0, "max": 100, "decimals": 8},
    "Impurity Concentration":    {"decimals": 8},
    "Allergen Concentration":    {"min": 0, "max": 100, "decimals": 8},
    "INCI Name":                 {"max_chars": 200},
    "Impurity Name":             {"max_chars": 200},
    "Allergen Name":             {"max_chars": 200},
    "INCI Function":             {"max_chars": 255},
    "Is Incidental?":            {"allowed": {"Yes", "No"}},
    "Is Locked":                 {"allowed": {"Yes", "No"}},
    "Impurity Concentration type (% or PPM)": {"allowed": {"%", "PPM"}},
}
