"""
tests/test_validate.py
Unit tests for etl/validate.py — covers every constraint in config.CONSTRAINTS.
"""
import pytest
import pandas as pd
from etl.validate import validate, _check_row


def make_df(**kwargs):
    """Build a single-row DataFrame with given column values."""
    return pd.DataFrame({k: [v] for k, v in kwargs.items()})


def make_valid_row():
    """Return a fully valid single-row DataFrame that passes all constraints."""
    return make_df(**{
        "Trade Name":                             "Valid Trade",
        "Manufacturer":                           "Corp",
        "Supplier&Distributor":                   "10001",
        "Reference Number":                       "10001",
        "INCI Name":                              "Water",
        "CAS INCI / Incidental":                  "10001",
        "Is Incidental?":                         "No",
        "INCI Concentration":                     50.0,
        "INCI Conc Min":                          10.0,
        "INCI Conc Max":                          90.0,
        "INCI Function":                          "Solvent",
        "Impurity Name":                          "Lead",
        "CAS Impurity":                           "10001",
        "Impurity Concentration":                 3.0,
        "Impurity Concentration type (% or PPM)": "PPM",
        "Allergen Name":                          "Limonene",
        "CAS Allergen":                           "10001",
        "Allergen Concentration":                 0.5,
        "RM Status":                              "Active",
        "Is Locked":                              "No",
        "Price":                                  None,
        "Price: From":                            None,
        "Price: To":                              None,
        "Description":                            None,
    })


# ── Validation column is added ───────────────────────────────────────────────

class TestValidationColumnAdded:
    def test_validation_column_exists(self):
        df, _ = validate(make_valid_row())
        assert "Validation" in df.columns

    def test_valid_row_is_ok(self):
        df, issues = validate(make_valid_row())
        assert df["Validation"].iloc[0] == "OK"
        assert len(issues) == 0

    def test_multiple_rows_all_ok(self):
        base = make_valid_row()
        df = pd.concat([base, base], ignore_index=True)
        df, issues = validate(df)
        assert all(df["Validation"] == "OK")
        assert len(issues) == 0


# ── Reference Number (max 30 chars) ──────────────────────────────────────────

class TestReferenceNumberConstraint:
    def test_exactly_30_chars_ok(self):
        df, issues = validate(make_df(**{"Reference Number": "1" * 30}))
        col_issues = [i for i in issues if i["column"] == "Reference Number"]
        assert len(col_issues) == 0

    def test_31_chars_fails(self):
        df, issues = validate(make_df(**{"Reference Number": "1" * 31}))
        col_issues = [i for i in issues if i["column"] == "Reference Number"]
        assert len(col_issues) == 1
        assert "max_chars" in col_issues[0]["rule"]

    def test_none_skipped(self):
        df, issues = validate(make_df(**{"Reference Number": None}))
        col_issues = [i for i in issues if i["column"] == "Reference Number"]
        assert len(col_issues) == 0


# ── INCI Concentration (0–100, max 8 decimals) ───────────────────────────────

class TestInciConcentrationConstraint:
    def test_zero_ok(self):
        df, issues = validate(make_df(**{"INCI Concentration": 0.0}))
        assert not any(i["column"] == "INCI Concentration" for i in issues)

    def test_100_ok(self):
        df, issues = validate(make_df(**{"INCI Concentration": 100.0}))
        assert not any(i["column"] == "INCI Concentration" for i in issues)

    def test_50_ok(self):
        df, issues = validate(make_df(**{"INCI Concentration": 50.0}))
        assert not any(i["column"] == "INCI Concentration" for i in issues)

    def test_above_100_fails(self):
        df, issues = validate(make_df(**{"INCI Concentration": 100.1}))
        col_issues = [i for i in issues if i["column"] == "INCI Concentration"]
        assert any("max" in i["rule"] for i in col_issues)

    def test_negative_fails(self):
        df, issues = validate(make_df(**{"INCI Concentration": -0.1}))
        col_issues = [i for i in issues if i["column"] == "INCI Concentration"]
        assert any("min" in i["rule"] for i in col_issues)

    def test_none_skipped(self):
        df, issues = validate(make_df(**{"INCI Concentration": None}))
        assert not any(i["column"] == "INCI Concentration" for i in issues)


# ── INCI Conc Min (0–100, max 8 decimals) ────────────────────────────────────

class TestInciConcMinConstraint:
    def test_valid_value(self):
        df, issues = validate(make_df(**{"INCI Conc Min": 10.0}))
        assert not any(i["column"] == "INCI Conc Min" for i in issues)

    def test_above_100_fails(self):
        df, issues = validate(make_df(**{"INCI Conc Min": 101.0}))
        col_issues = [i for i in issues if i["column"] == "INCI Conc Min"]
        assert len(col_issues) > 0

    def test_negative_fails(self):
        df, issues = validate(make_df(**{"INCI Conc Min": -1.0}))
        col_issues = [i for i in issues if i["column"] == "INCI Conc Min"]
        assert len(col_issues) > 0

    def test_none_skipped(self):
        df, issues = validate(make_df(**{"INCI Conc Min": None}))
        assert not any(i["column"] == "INCI Conc Min" for i in issues)


# ── INCI Conc Max (0–100, max 8 decimals) ────────────────────────────────────

class TestInciConcMaxConstraint:
    def test_valid_value(self):
        df, issues = validate(make_df(**{"INCI Conc Max": 90.0}))
        assert not any(i["column"] == "INCI Conc Max" for i in issues)

    def test_above_100_fails(self):
        df, issues = validate(make_df(**{"INCI Conc Max": 100.5}))
        col_issues = [i for i in issues if i["column"] == "INCI Conc Max"]
        assert len(col_issues) > 0

    def test_zero_ok(self):
        df, issues = validate(make_df(**{"INCI Conc Max": 0.0}))
        assert not any(i["column"] == "INCI Conc Max" for i in issues)


# ── Impurity Concentration (max 8 decimals, no range restriction) ─────────────

class TestImpurityConcentrationConstraint:
    def test_valid_small(self):
        df, issues = validate(make_df(**{"Impurity Concentration": 0.0001}))
        assert not any(i["column"] == "Impurity Concentration" for i in issues)

    def test_large_value_ok(self):
        # No max restriction on impurity concentration
        df, issues = validate(make_df(**{"Impurity Concentration": 99999.0}))
        assert not any(i["column"] == "Impurity Concentration" for i in issues)

    def test_none_skipped(self):
        df, issues = validate(make_df(**{"Impurity Concentration": None}))
        assert not any(i["column"] == "Impurity Concentration" for i in issues)

    def test_non_numeric_fails(self):
        df, issues = validate(make_df(**{"Impurity Concentration": "not a number"}))
        col_issues = [i for i in issues if i["column"] == "Impurity Concentration"]
        assert len(col_issues) > 0


# ── Allergen Concentration (0–100, max 8 decimals) ───────────────────────────

class TestAllergenConcentrationConstraint:
    def test_valid_value(self):
        df, issues = validate(make_df(**{"Allergen Concentration": 5.0}))
        assert not any(i["column"] == "Allergen Concentration" for i in issues)

    def test_zero_ok(self):
        df, issues = validate(make_df(**{"Allergen Concentration": 0.0}))
        assert not any(i["column"] == "Allergen Concentration" for i in issues)

    def test_100_ok(self):
        df, issues = validate(make_df(**{"Allergen Concentration": 100.0}))
        assert not any(i["column"] == "Allergen Concentration" for i in issues)

    def test_above_100_fails(self):
        df, issues = validate(make_df(**{"Allergen Concentration": 100.1}))
        col_issues = [i for i in issues if i["column"] == "Allergen Concentration"]
        assert len(col_issues) > 0

    def test_negative_fails(self):
        df, issues = validate(make_df(**{"Allergen Concentration": -1.0}))
        col_issues = [i for i in issues if i["column"] == "Allergen Concentration"]
        assert len(col_issues) > 0

    def test_none_skipped(self):
        df, issues = validate(make_df(**{"Allergen Concentration": None}))
        assert not any(i["column"] == "Allergen Concentration" for i in issues)


# ── INCI Name max 200 chars ──────────────────────────────────────────────────

class TestInciNameConstraint:
    def test_exactly_200_ok(self):
        df, issues = validate(make_df(**{"INCI Name": "A" * 200}))
        assert not any(i["column"] == "INCI Name" for i in issues)

    def test_201_fails(self):
        df, issues = validate(make_df(**{"INCI Name": "A" * 201}))
        col_issues = [i for i in issues if i["column"] == "INCI Name"]
        assert len(col_issues) > 0

    def test_none_skipped(self):
        df, issues = validate(make_df(**{"INCI Name": None}))
        assert not any(i["column"] == "INCI Name" for i in issues)


# ── Impurity Name max 200 chars ──────────────────────────────────────────────

class TestImpurityNameConstraint:
    def test_valid(self):
        df, issues = validate(make_df(**{"Impurity Name": "Lead"}))
        assert not any(i["column"] == "Impurity Name" for i in issues)

    def test_too_long_fails(self):
        df, issues = validate(make_df(**{"Impurity Name": "X" * 201}))
        col_issues = [i for i in issues if i["column"] == "Impurity Name"]
        assert len(col_issues) > 0


# ── Allergen Name max 200 chars ──────────────────────────────────────────────

class TestAllergenNameConstraint:
    def test_valid(self):
        df, issues = validate(make_df(**{"Allergen Name": "Limonene"}))
        assert not any(i["column"] == "Allergen Name" for i in issues)

    def test_too_long_fails(self):
        df, issues = validate(make_df(**{"Allergen Name": "Y" * 201}))
        col_issues = [i for i in issues if i["column"] == "Allergen Name"]
        assert len(col_issues) > 0


# ── INCI Function max 255 chars ──────────────────────────────────────────────

class TestInciFunctionConstraint:
    def test_exactly_255_ok(self):
        df, issues = validate(make_df(**{"INCI Function": "S" * 255}))
        assert not any(i["column"] == "INCI Function" for i in issues)

    def test_256_fails(self):
        df, issues = validate(make_df(**{"INCI Function": "S" * 256}))
        col_issues = [i for i in issues if i["column"] == "INCI Function"]
        assert len(col_issues) > 0


# ── Is Incidental? allowed values ────────────────────────────────────────────

class TestIsIncidentalConstraint:
    def test_yes_ok(self):
        df, issues = validate(make_df(**{"Is Incidental?": "Yes"}))
        assert not any(i["column"] == "Is Incidental?" for i in issues)

    def test_no_ok(self):
        df, issues = validate(make_df(**{"Is Incidental?": "No"}))
        assert not any(i["column"] == "Is Incidental?" for i in issues)

    def test_y_fails(self):
        df, issues = validate(make_df(**{"Is Incidental?": "Y"}))
        col_issues = [i for i in issues if i["column"] == "Is Incidental?"]
        assert len(col_issues) > 0

    def test_true_fails(self):
        df, issues = validate(make_df(**{"Is Incidental?": "TRUE"}))
        col_issues = [i for i in issues if i["column"] == "Is Incidental?"]
        assert len(col_issues) > 0


# ── Is Locked allowed values ─────────────────────────────────────────────────

class TestIsLockedConstraint:
    def test_yes_ok(self):
        df, issues = validate(make_df(**{"Is Locked": "Yes"}))
        assert not any(i["column"] == "Is Locked" for i in issues)

    def test_no_ok(self):
        df, issues = validate(make_df(**{"Is Locked": "No"}))
        assert not any(i["column"] == "Is Locked" for i in issues)

    def test_false_fails(self):
        df, issues = validate(make_df(**{"Is Locked": "false"}))
        col_issues = [i for i in issues if i["column"] == "Is Locked"]
        assert len(col_issues) > 0


# ── Impurity Concentration type ──────────────────────────────────────────────

class TestImpurityConcentrationTypeConstraint:
    def test_ppm_ok(self):
        df, issues = validate(make_df(**{"Impurity Concentration type (% or PPM)": "PPM"}))
        assert not any(i["column"] == "Impurity Concentration type (% or PPM)" for i in issues)

    def test_percent_ok(self):
        df, issues = validate(make_df(**{"Impurity Concentration type (% or PPM)": "%"}))
        assert not any(i["column"] == "Impurity Concentration type (% or PPM)" for i in issues)

    def test_ppm_lowercase_fails(self):
        df, issues = validate(make_df(**{"Impurity Concentration type (% or PPM)": "ppm"}))
        col_issues = [i for i in issues if i["column"] == "Impurity Concentration type (% or PPM)"]
        assert len(col_issues) > 0

    def test_percent_word_fails(self):
        df, issues = validate(make_df(**{"Impurity Concentration type (% or PPM)": "percent"}))
        col_issues = [i for i in issues if i["column"] == "Impurity Concentration type (% or PPM)"]
        assert len(col_issues) > 0


# ── Issue structure ──────────────────────────────────────────────────────────

class TestIssueStructure:
    def test_issue_has_required_keys(self):
        df, issues = validate(make_df(**{"Is Locked": "WRONG"}))
        assert len(issues) > 0
        issue = issues[0]
        assert "row"    in issue
        assert "column" in issue
        assert "value"  in issue
        assert "rule"   in issue
        assert "detail" in issue

    def test_issue_row_flagged(self):
        df, issues = validate(make_df(**{"Is Locked": "WRONG"}))
        assert df["Validation"].iloc[0] == "ISSUE"

    def test_multiple_violations_same_row(self):
        df, issues = validate(make_df(**{
            "Is Incidental?": "WRONG",
            "Is Locked":      "WRONG",
        }))
        assert df["Validation"].iloc[0] == "ISSUE"
        assert len(issues) >= 2

    def test_only_bad_row_flagged(self):
        good = make_valid_row()
        bad  = make_df(**{"Is Locked": "WRONG"})
        df   = pd.concat([good, bad], ignore_index=True)
        df, issues = validate(df)
        assert df["Validation"].iloc[0] == "OK"
        assert df["Validation"].iloc[1] == "ISSUE"

    def test_custom_constraints(self):
        """validate() accepts custom constraint dict."""
        custom = {"Reference Number": {"max_chars": 5}}
        df, issues = validate(make_df(**{"Reference Number": "123456"}), constraints=custom)
        assert len(issues) == 1
        assert issues[0]["column"] == "Reference Number"
