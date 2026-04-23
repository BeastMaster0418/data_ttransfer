"""
tests/test_extract.py
Tests for etl/extract.py
"""
import pytest
import pandas as pd
from pathlib import Path
from etl.extract import load_data
from config import EXTRACTION_FILE, CUSTOMER_FILE


# ── Using real files (integration) ──────────────────────────────────────────

class TestLoadDataIntegration:
    def test_returns_two_dataframes(self):
        extraction, customer = load_data()
        assert isinstance(extraction, pd.DataFrame)
        assert isinstance(customer, pd.DataFrame)

    def test_extraction_has_expected_columns(self):
        extraction, _ = load_data()
        expected = {
            "Reference Number", "Trade Name", "Manufacturer",
            "INCI", "INCI Comp", "Incidental?",
            "Impurity", "Impurity Comp",
            "Allergens", "Allergen Comp", "Function",
        }
        assert expected.issubset(set(extraction.columns))

    def test_customer_has_expected_columns(self):
        _, customer = load_data()
        expected = {"Item ID", "Client Preferred Trade Name", "Status"}
        assert expected.issubset(set(customer.columns))

    def test_extraction_has_rows(self):
        extraction, _ = load_data()
        assert len(extraction) > 0

    def test_customer_has_rows(self):
        _, customer = load_data()
        assert len(customer) > 0

    def test_extraction_row_count(self):
        extraction, _ = load_data()
        assert len(extraction) == 6231

    def test_customer_row_count(self):
        _, customer = load_data()
        assert len(customer) == 2747


# ── Custom path arguments ────────────────────────────────────────────────────

class TestLoadDataCustomPaths:
    def test_explicit_paths_work(self):
        extraction, customer = load_data(
            extraction_path=EXTRACTION_FILE,
            customer_path=CUSTOMER_FILE,
        )
        assert len(extraction) > 0
        assert len(customer) > 0

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(Exception):
            load_data(
                extraction_path=tmp_path / "nonexistent.xlsx",
                customer_path=CUSTOMER_FILE,
            )
