# backend/app/services/sales_reader.py

import pandas as pd

def read_sales_file(file_path):
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        raise Exception("Unsupported file format")

    df.columns = [c.lower().strip() for c in df.columns]
    return df
