import pandas as pd
from pathlib import Path
from config import OUTPUT_FILE, OUTPUT_COLUMNS


def save_output(
    df: pd.DataFrame,
    output_path=OUTPUT_FILE,
    include_validation: bool = False,
) -> Path:
    """
    Write the transformed DataFrame to an Excel file.

    Parameters
    ----------
    df                  : transformed (and optionally validated) DataFrame
    output_path         : destination .xlsx path  (default: config.OUTPUT_FILE)
    include_validation  : if True, keep the 'Validation' column in the output

    Returns
    -------
    Path to the saved file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cols = list(OUTPUT_COLUMNS)
    if include_validation and "Validation" in df.columns:
        cols = cols + ["Validation"]

    df[cols].to_excel(output_path, index=False)
    return output_path
