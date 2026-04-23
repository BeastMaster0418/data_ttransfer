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
    raw_extraction_data = pd.read_excel(extraction_path)
    customer_rm_list   = pd.read_excel(customer_path)
    return raw_extraction_data, customer_rm_list
