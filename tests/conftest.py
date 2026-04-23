"""
Shared pytest fixtures for the ETL test suite.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

# Make project root importable
sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Minimal extraction DataFrame ────────────────────────────────────────────

@pytest.fixture
def extraction_single():
    """One product row with full data."""
    return pd.DataFrame({
        "Reference Number": [10001.0],
        "Trade Name":       ["Product Alpha"],
        "Manufacturer":     ["ACME Corp"],
        "INCI":             ["Water"],
        "INCI Comp":        [100],
        "Incidental?":      [None],
        "Impurity":         ["Lead"],
        "Impurity Comp":    ["< 3 ppm"],
        "Allergens":        ["Limonene"],
        "Allergen Comp":    [0.5],
        "Function":         ["Solvent"],
        "Notes":            [None],
        "GROUP":            [1.0],
        "Missing Comp":     [None],
        "SDS Comp":         [None],
    })


@pytest.fixture
def extraction_multi_row():
    """Parent row + two sub-rows sharing the same reference number."""
    return pd.DataFrame({
        "Reference Number": [10005.0,         None,             None],
        "Trade Name":       ["SOLAGUM AX",     None,             None],
        "Manufacturer":     ["Seppic",          None,             None],
        "INCI":             ["Acacia Senegal",  "Xanthan Gum",   None],
        "INCI Comp":        ["51 - 59",         "41 - 49",       None],
        "Incidental?":      [None,              None,            None],
        "Impurity":         [None,              "Water",         "Lead"],
        "Impurity Comp":    [None,              "< 12",          "< 2 ppm"],
        "Allergens":        [None,              None,            None],
        "Allergen Comp":    [None,              None,            None],
        "Function":         ["Viscosity increasing agent", None, None],
        "Notes":            [None,              None,            None],
        "GROUP":            [1.0,               None,            None],
        "Missing Comp":     [None,              None,            None],
        "SDS Comp":         [None,              None,            None],
    })


@pytest.fixture
def extraction_no_ref():
    """Row where reference number is missing and must be forward-filled."""
    return pd.DataFrame({
        "Reference Number": [10002.0, None,    None],
        "Trade Name":       ["Prod B", None,    None],
        "Manufacturer":     ["Corp X", None,    None],
        "INCI":             ["Glycerin", "Aqua", None],
        "INCI Comp":        [80,          20,    None],
        "Incidental?":      [None,        None,  None],
        "Impurity":         [None,        None,  None],
        "Impurity Comp":    [None,        None,  None],
        "Allergens":        [None,        None,  None],
        "Allergen Comp":    [None,        None,  None],
        "Function":         [None,        None,  None],
        "Notes":            [None,        None,  None],
        "GROUP":            [1.0,         None,  None],
        "Missing Comp":     [None,        None,  None],
        "SDS Comp":         [None,        None,  None],
    })


@pytest.fixture
def customer_basic():
    """Matching customer lookup row."""
    return pd.DataFrame({
        "Item ID": ["GFP-10001"],
        "Client Preferred Trade Name": ["Acetamide MEA 75%"],
        "Status": ["Active"],
        "Additional Description": [None],
        "Average Cost": [0.0],
        "Last Cost": [0.0],
        "Qty On Hand": [0.0],
    })


@pytest.fixture
def customer_multi():
    """Multiple customer rows for different reference numbers."""
    return pd.DataFrame({
        "Item ID": ["GFP-10001", "GFP-10002", "GFP-10005"],
        "Client Preferred Trade Name": ["Trade Alpha", "Trade Beta", "Trade Gamma"],
        "Status": ["Active", "Inactive", "Active"],
        "Additional Description": [None, None, None],
        "Average Cost": [0.0, 0.0, 0.0],
        "Last Cost": [0.0, 0.0, 0.0],
        "Qty On Hand": [0.0, 0.0, 0.0],
    })


@pytest.fixture
def customer_empty():
    """Customer table with no rows."""
    return pd.DataFrame({
        "Item ID": pd.Series([], dtype=str),
        "Client Preferred Trade Name": pd.Series([], dtype=str),
        "Status": pd.Series([], dtype=str),
        "Additional Description": pd.Series([], dtype=str),
        "Average Cost": pd.Series([], dtype=float),
        "Last Cost": pd.Series([], dtype=float),
        "Qty On Hand": pd.Series([], dtype=float),
    })
