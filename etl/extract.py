import pandas as pd
from config import EXTRACTION_FILE, CUSTOMER_FILE


def load_data(
    extraction_path=EXTRACTION_FILE,
    customer_path=CUSTOMER_FILE,
):
    """
    Load raw source files.

    Returns
    -------
    extraction : pd.DataFrame   (Extraction File – Sheet: Original)
    customer   : pd.DataFrame   (Customer Supplied RM List)
    """
    extraction = pd.read_excel(extraction_path)
    customer   = pd.read_excel(customer_path)
    return extraction, customer
