"""
tests/test_parsers.py
Unit tests for utils/parsers.py
"""
import math
import pytest
from utils.parsers import (
    extract_number_max,
    extract_impurity_unit,
    parse_inci_comp,
    extract_allergen_max,
)


# ── extract_number_max ───────────────────────────────────────────────────────

class TestExtractNumberMax:
    # Plain numeric
    def test_plain_integer(self):
        assert extract_number_max(100) == 100.0

    def test_plain_float(self):
        assert extract_number_max(3.5) == 3.5

    def test_plain_string_number(self):
        assert extract_number_max("25") == 25.0

    # Less-than prefix
    def test_less_than(self):
        assert extract_number_max("< 3") == 3.0

    def test_less_than_ppm(self):
        assert extract_number_max("< 3 ppm") == 3.0

    def test_less_than_no_space(self):
        assert extract_number_max("<3") == 3.0

    def test_less_than_equal(self):
        assert extract_number_max("<= 1 ppm") == 1.0

    # Max prefix
    def test_max_prefix(self):
        assert extract_number_max("max 1 ppm") == 1.0

    def test_max_dot_prefix(self):
        assert extract_number_max("max. 5 ppm") == 5.0

    def test_max_uppercase(self):
        assert extract_number_max("Max 20 ppm") == 20.0

    # Range → upper bound
    def test_range_returns_max(self):
        assert extract_number_max("4 - 6") == 6.0

    def test_range_ppm(self):
        assert extract_number_max("1 - 3 ppm") == 3.0

    def test_range_decimal(self):
        assert extract_number_max("0.1 - 0.3") == 0.3

    def test_range_with_en_dash(self):
        assert extract_number_max("4–6") == 6.0

    # Units
    def test_ppb_unit(self):
        assert extract_number_max("< 10 ppb") == 10.0

    def test_mg_kg_unit(self):
        assert extract_number_max("< 5 mg/kg") == 5.0

    def test_percent_unit(self):
        assert extract_number_max("< 0.5%") == 0.5

    # Trailing max
    def test_trailing_ppm_max(self):
        assert extract_number_max("10 ppm max") == 10.0

    def test_trailing_max_dot(self):
        assert extract_number_max("5 ppm max.") == 5.0

    # NMT prefix
    def test_nmt_prefix(self):
        assert extract_number_max("NMT 1 ppm") == 1.0

    # Edge cases
    def test_none_returns_none(self):
        assert extract_number_max(None) is None

    def test_nan_returns_none(self):
        assert extract_number_max(float("nan")) is None

    def test_decimal_precision(self):
        result = extract_number_max("< 0.00000001")
        assert result == pytest.approx(1e-8)

    def test_large_ppm(self):
        assert extract_number_max("< 5000 ppm") == 5000.0


# ── extract_impurity_unit ────────────────────────────────────────────────────

class TestExtractImpurityUnit:
    def test_ppm_lowercase(self):
        assert extract_impurity_unit("< 3 ppm") == "PPM"

    def test_ppm_uppercase(self):
        assert extract_impurity_unit("< 3 PPM") == "PPM"

    def test_ppb(self):
        assert extract_impurity_unit("< 10 ppb") == "PPM"

    def test_mg_kg(self):
        assert extract_impurity_unit("< 5 mg/kg") == "PPM"

    def test_ug_kg(self):
        assert extract_impurity_unit("< 2 ug/kg") == "PPM"

    def test_mg_l(self):
        assert extract_impurity_unit("0.5 mg/L") == "PPM"

    def test_plain_number_returns_percent(self):
        assert extract_impurity_unit("< 0.5") == "%"

    def test_percent_sign_returns_percent(self):
        assert extract_impurity_unit("< 0.5%") == "%"

    def test_none_returns_none(self):
        assert extract_impurity_unit(None) is None

    def test_nan_returns_none(self):
        assert extract_impurity_unit(float("nan")) is None

    def test_max_ppm(self):
        assert extract_impurity_unit("max 1 ppm") == "PPM"

    def test_range_no_unit(self):
        assert extract_impurity_unit("4 - 6") == "%"

    def test_range_with_ppm(self):
        assert extract_impurity_unit("1 - 3 ppm") == "PPM"


# ── parse_inci_comp ──────────────────────────────────────────────────────────

class TestParseInciComp:
    # Exact values
    def test_exact_integer(self):
        exact, lo, hi = parse_inci_comp(100)
        assert exact == 100.0
        assert lo is None
        assert hi is None

    def test_exact_string_int(self):
        exact, lo, hi = parse_inci_comp("100")
        assert exact == 100.0

    def test_exact_float(self):
        exact, lo, hi = parse_inci_comp("28.5")
        assert exact == pytest.approx(28.5)

    # Range values
    def test_range_simple(self):
        exact, lo, hi = parse_inci_comp("51 - 59")
        assert exact is None
        assert lo == 51.0
        assert hi == 59.0

    def test_range_decimal(self):
        exact, lo, hi = parse_inci_comp("22.5 - 37.5")
        assert lo == pytest.approx(22.5)
        assert hi == pytest.approx(37.5)

    def test_range_en_dash(self):
        exact, lo, hi = parse_inci_comp("41–49")
        assert lo == 41.0
        assert hi == 49.0

    def test_range_small(self):
        exact, lo, hi = parse_inci_comp("0.0004 - 0.0008")
        assert lo == pytest.approx(0.0004)
        assert hi == pytest.approx(0.0008)

    # Inequality values
    def test_less_than(self):
        exact, lo, hi = parse_inci_comp("< 5")
        assert exact is None
        assert lo is None
        assert hi == 5.0

    def test_less_than_equal(self):
        exact, lo, hi = parse_inci_comp("<= 0.2")
        assert hi == pytest.approx(0.2)

    def test_greater_than(self):
        exact, lo, hi = parse_inci_comp("> 50")
        assert exact is None
        assert lo == 50.0
        assert hi is None

    def test_greater_than_equal(self):
        exact, lo, hi = parse_inci_comp(">= 97")
        assert lo == 97.0

    # Null handling
    def test_none_returns_triple_none(self):
        assert parse_inci_comp(None) == (None, None, None)

    def test_nan_returns_triple_none(self):
        assert parse_inci_comp(float("nan")) == (None, None, None)

    # Rounding
    def test_rounds_to_8_decimals(self):
        exact, _, _ = parse_inci_comp("99.123456789")
        assert exact == round(99.123456789, 8)


# ── extract_allergen_max ─────────────────────────────────────────────────────

class TestExtractAllergenMax:
    # Plain numbers
    def test_plain_float(self):
        assert extract_allergen_max(0.5) == 0.5

    def test_plain_integer(self):
        assert extract_allergen_max(49) == 49.0

    def test_plain_string(self):
        assert extract_allergen_max("3.5") == 3.5

    # Range → upper bound
    def test_range_returns_max(self):
        assert extract_allergen_max("1 - 3") == 3.0

    def test_range_decimal(self):
        assert extract_allergen_max("0.4 - 1.2") == pytest.approx(1.2)

    def test_range_en_dash(self):
        assert extract_allergen_max("25–40") == 40.0

    # Prefix operators
    def test_less_than(self):
        assert extract_allergen_max("< 1") == 1.0

    def test_less_than_2(self):
        assert extract_allergen_max("< 2") == 2.0

    def test_greater_than_50(self):
        assert extract_allergen_max("> 50") == 50.0

    def test_max_prefix(self):
        assert extract_allergen_max("MAX 0.3") == pytest.approx(0.3)

    def test_max_uppercase(self):
        assert extract_allergen_max("MAX 1.0") == pytest.approx(1.0)

    # Incompatible units → None
    def test_ug_kg_returns_none(self):
        assert extract_allergen_max("150 μg/kg") is None

    def test_mg_kg_returns_none(self):
        assert extract_allergen_max("5 mg/kg") is None

    def test_mg_l_returns_none(self):
        assert extract_allergen_max("0.5 mg/l") is None

    # Null handling
    def test_none_returns_none(self):
        assert extract_allergen_max(None) is None

    def test_nan_returns_none(self):
        assert extract_allergen_max(float("nan")) is None

    # Precision
    def test_small_decimal(self):
        assert extract_allergen_max(0.00525) == pytest.approx(0.00525)

    def test_rounds_to_8_decimals(self):
        result = extract_allergen_max(1.123456789)
        assert result == round(1.123456789, 8)
