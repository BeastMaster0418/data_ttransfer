"""
tests/test_helpers.py
Unit tests for utils/helpers.py
"""
import math
import pytest
import pandas as pd
from utils.helpers import (
    safe_float,
    clean_text,
    safe_ref,
    incidental_flag,
    semi_colon_join,
    clamp_0_100,
    limit_decimals,
)


# ── safe_float ───────────────────────────────────────────────────────────────

class TestSafeFloat:
    def test_integer_string(self):
        assert safe_float("42") == 42.0

    def test_float_string(self):
        assert safe_float("3.14") == 3.14

    def test_numeric_int(self):
        assert safe_float(10) == 10.0

    def test_numeric_float(self):
        assert safe_float(0.5) == 0.5

    def test_none_returns_none(self):
        assert safe_float(None) is None

    def test_invalid_string_returns_none(self):
        assert safe_float("abc") is None

    def test_empty_string_returns_none(self):
        assert safe_float("") is None

    def test_infinity_returns_none(self):
        assert safe_float(float("inf")) is None

    def test_nan_returns_none(self):
        assert safe_float(float("nan")) is None

    def test_scientific_notation(self):
        assert safe_float("1e-5") == pytest.approx(1e-5)


# ── clean_text ───────────────────────────────────────────────────────────────

class TestCleanText:
    def test_strips_whitespace(self):
        assert clean_text("  hello  ") == "hello"

    def test_truncates_to_max_len(self):
        assert clean_text("abcdef", max_len=3) == "abc"

    def test_no_truncation_when_no_max(self):
        assert clean_text("abcdef") == "abcdef"

    def test_none_returns_none(self):
        assert clean_text(None) is None

    def test_nan_returns_none(self):
        assert clean_text(float("nan")) is None

    def test_converts_non_string(self):
        assert clean_text(12345) == "12345"

    def test_exact_length_boundary(self):
        assert clean_text("abc", max_len=3) == "abc"

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_max_len_200(self):
        long = "x" * 250
        assert len(clean_text(long, max_len=200)) == 200

    def test_max_len_255(self):
        long = "y" * 300
        assert len(clean_text(long, max_len=255)) == 255


# ── safe_ref ─────────────────────────────────────────────────────────────────

class TestSafeRef:
    def test_float_to_int_string(self):
        assert safe_ref(10001.0) == "10001"

    def test_integer(self):
        assert safe_ref(10002) == "10002"

    def test_string_numeric(self):
        assert safe_ref("10003") == "10003"

    def test_none_returns_none(self):
        assert safe_ref(None) is None

    def test_nan_returns_none(self):
        assert safe_ref(float("nan")) is None

    def test_truncates_to_30_chars(self):
        # Non-numeric string is truncated directly to 30 chars
        long_ref = "X" * 40
        result = safe_ref(long_ref)
        assert len(result) == 30
        assert result == "X" * 30

    def test_exactly_30_chars(self):
        ref = "1" * 30
        assert safe_ref(ref) == ref

    def test_alphanumeric_string(self):
        assert safe_ref("GFP-10001") == "GFP-10001"


# ── incidental_flag ──────────────────────────────────────────────────────────

class TestIncidentalFlag:
    def test_y_uppercase(self):
        assert incidental_flag("Y") == "Yes"

    def test_y_lowercase(self):
        assert incidental_flag("y") == "Yes"

    def test_yes_string(self):
        assert incidental_flag("YES") == "Yes"

    def test_yes_mixed_case(self):
        assert incidental_flag("Yes") == "Yes"

    def test_one_string(self):
        assert incidental_flag("1") == "Yes"

    def test_true_string(self):
        assert incidental_flag("TRUE") == "Yes"

    def test_none_returns_no(self):
        assert incidental_flag(None) == "No"

    def test_nan_returns_no(self):
        assert incidental_flag(float("nan")) == "No"

    def test_n_returns_no(self):
        assert incidental_flag("N") == "No"

    def test_no_string_returns_no(self):
        assert incidental_flag("NO") == "No"

    def test_empty_string_returns_no(self):
        assert incidental_flag("") == "No"

    def test_zero_returns_no(self):
        assert incidental_flag("0") == "No"

    def test_false_string_returns_no(self):
        assert incidental_flag("FALSE") == "No"


# ── semi_colon_join ──────────────────────────────────────────────────────────

class TestSemiColonJoin:
    def test_single_value(self):
        assert semi_colon_join("Solvent") == "Solvent"

    def test_comma_separated(self):
        assert semi_colon_join("Solvent, Emulsifier") == "Solvent; Emulsifier"

    def test_semicolon_separated(self):
        assert semi_colon_join("Solvent; Emulsifier") == "Solvent; Emulsifier"

    def test_mixed_separators(self):
        result = semi_colon_join("Solvent, Emulsifier; Thickener")
        assert result == "Solvent; Emulsifier; Thickener"

    def test_none_returns_none(self):
        assert semi_colon_join(None) is None

    def test_nan_returns_none(self):
        assert semi_colon_join(float("nan")) is None

    def test_truncates_to_255(self):
        long = ", ".join(["word"] * 100)
        result = semi_colon_join(long, max_len=255)
        assert len(result) <= 255

    def test_strips_extra_whitespace(self):
        assert semi_colon_join("  Solvent  ,  Emulsifier  ") == "Solvent; Emulsifier"

    def test_empty_parts_skipped(self):
        assert semi_colon_join("Solvent,,Emulsifier") == "Solvent; Emulsifier"


# ── clamp_0_100 ──────────────────────────────────────────────────────────────

class TestClamp0100:
    def test_zero_boundary(self):
        assert clamp_0_100(0) == 0.0

    def test_hundred_boundary(self):
        assert clamp_0_100(100) == 100.0

    def test_midrange_value(self):
        assert clamp_0_100(50.0) == 50.0

    def test_above_100_returns_none(self):
        assert clamp_0_100(100.1) is None

    def test_negative_returns_none(self):
        assert clamp_0_100(-0.1) is None

    def test_none_returns_none(self):
        assert clamp_0_100(None) is None

    def test_rounds_to_8_decimals(self):
        result = clamp_0_100(50.123456789)
        assert result == round(50.123456789, 8)

    def test_small_positive(self):
        assert clamp_0_100(0.00000001) == 0.00000001

    def test_exact_100(self):
        assert clamp_0_100(100.0) == 100.0


# ── limit_decimals ───────────────────────────────────────────────────────────

class TestLimitDecimals:
    def test_rounds_to_8(self):
        assert limit_decimals(1.123456789) == round(1.123456789, 8)

    def test_none_returns_none(self):
        assert limit_decimals(None) is None

    def test_integer_value(self):
        assert limit_decimals(5) == 5.0

    def test_zero(self):
        assert limit_decimals(0) == 0.0

    def test_custom_decimals(self):
        assert limit_decimals(1.99999999999, 4) == round(1.99999999999, 4)

    def test_large_value(self):
        assert limit_decimals(999999.12345678) == round(999999.12345678, 8)
