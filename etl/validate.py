import pandas as pd
from config import CONSTRAINTS


def _check_row(idx: int, row: pd.Series, constraints: dict) -> list[dict]:
    """Validate a single row against all constraints. Returns list of issue dicts."""
    issues = []

    for col, rules in constraints.items():
        val = row.get(col)

        # Skip None / NaN – presence is not enforced here
        if val is None or (isinstance(val, float) and pd.isna(val)):
            continue

        # max_chars
        if "max_chars" in rules and isinstance(val, str):
            if len(val) > rules["max_chars"]:
                issues.append({
                    "row":    idx,
                    "column": col,
                    "value":  val,
                    "rule":   f"max_chars={rules['max_chars']}",
                    "detail": f"Length {len(val)} exceeds {rules['max_chars']}",
                })

        # numeric range & decimals
        if "min" in rules or "max" in rules or "decimals" in rules:
            try:
                num = float(val)
            except (TypeError, ValueError):
                issues.append({
                    "row":    idx,
                    "column": col,
                    "value":  val,
                    "rule":   "numeric",
                    "detail": "Expected a numeric value",
                })
                continue

            if "min" in rules and num < rules["min"]:
                issues.append({
                    "row":    idx,
                    "column": col,
                    "value":  val,
                    "rule":   f"min={rules['min']}",
                    "detail": f"{num} is below minimum {rules['min']}",
                })

            if "max" in rules and num > rules["max"]:
                issues.append({
                    "row":    idx,
                    "column": col,
                    "value":  val,
                    "rule":   f"max={rules['max']}",
                    "detail": f"{num} exceeds maximum {rules['max']}",
                })

            if "decimals" in rules:
                s = str(val)
                if "." in s:
                    decimal_places = len(s.rstrip("0").split(".")[-1])
                    if decimal_places > rules["decimals"]:
                        issues.append({
                            "row":    idx,
                            "column": col,
                            "value":  val,
                            "rule":   f"decimals={rules['decimals']}",
                            "detail": f"{decimal_places} decimal places exceed limit",
                        })

        # allowed values
        if "allowed" in rules:
            if str(val) not in rules["allowed"]:
                issues.append({
                    "row":    idx,
                    "column": col,
                    "value":  val,
                    "rule":   f"allowed={rules['allowed']}",
                    "detail": f"'{val}' is not in allowed set {rules['allowed']}",
                })

    return issues


def validate(df: pd.DataFrame, constraints: dict = CONSTRAINTS) -> tuple[pd.DataFrame, list[dict]]:
    """
    Validate every row of *df* against *constraints*.

    Returns
    -------
    df     : original DataFrame with an added 'Validation' column ('OK' / 'ISSUE')
    issues : list of dicts describing every violation found
    """
    all_issues: list[dict] = []

    for idx, row in df.iterrows():
        row_issues = _check_row(idx, row, constraints)
        all_issues.extend(row_issues)

    flagged = {issue["row"] for issue in all_issues}
    df = df.copy()
    df["Validation"] = df.index.map(lambda i: "ISSUE" if i in flagged else "OK")

    return df, all_issues
