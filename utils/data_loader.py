import pandas as pd
import json

DEFAULT_DATASET = [
    {"month": "Jan", "sales": 42000, "customers": 320, "returns": 12},
    {"month": "Feb", "sales": 45000, "customers": 350, "returns": 15},
    {"month": "Mar", "sales": 54000, "customers": 410, "returns": 18},
    {"month": "Apr", "sales": 48000, "customers": 380, "returns": 10},
    {"month": "May", "sales": 60000, "customers": 450, "returns": 22},
    {"month": "Jun", "sales": 72000, "customers": 530, "returns": 21},
    {"month": "Jul", "sales": 68000, "customers": 500, "returns": 19},
    {"month": "Aug", "sales": 65000, "customers": 480, "returns": 17},
    {"month": "Sep", "sales": 70000, "customers": 520, "returns": 25},
    {"month": "Oct", "sales": 78000, "customers": 580, "returns": 20},
    {"month": "Nov", "sales": 90000, "customers": 690, "returns": 28},
    {"month": "Dec", "sales": 105000, "customers": 790, "returns": 31}
]

def get_default_df() -> pd.DataFrame:
    """Returns the default retail sales 12-month dataset as a Pandas DataFrame."""
    return pd.DataFrame(DEFAULT_DATASET)

def get_dataset_stats_summary(df: pd.DataFrame) -> str:
    """
    Computes summary metadata for the DataFrame to be included in the LLM system prompt.
    This helps the LLM understand the schema, rows, and general statistics immediately.
    """
    num_rows = len(df)
    columns = list(df.columns)
    
    # Identify numeric and categorical columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
    
    summary = []
    summary.append(f"Dataset shape: {num_rows} rows x {len(columns)} columns.")
    summary.append(f"Columns: {', '.join(columns)}")
    summary.append(f"Numeric columns: {', '.join(numeric_cols)}")
    summary.append(f"Categorical/Text columns: {', '.join(categorical_cols)}")
    
    # Brief stats for numeric columns
    if numeric_cols:
        summary.append("\nQuick Column Statistics:")
        for col in numeric_cols:
            col_min = df[col].min()
            col_max = df[col].max()
            col_sum = df[col].sum()
            col_mean = df[col].mean()
            # Format nicely
            if isinstance(col_min, (int, float)) and col_min > 1000:
                summary.append(f" - {col}: range [{col_min:,.0f} to {col_max:,.0f}], total={col_sum:,.0f}, avg={col_mean:,.1f}")
            else:
                summary.append(f" - {col}: range [{col_min} to {col_max}], total={col_sum}, avg={col_mean:.1f}")
                
    return "\n".join(summary)

def get_dataset_json(df: pd.DataFrame) -> str:
    """Converts the DataFrame to a JSON string formatted for injection in LLM prompt."""
    return df.to_json(orient="records", indent=2)

def validate_uploaded_csv(file) -> pd.DataFrame:
    """
    Reads an uploaded CSV file, validates it has at least some data,
    and returns a clean Pandas DataFrame. Raises ValueError on failure.
    """
    try:
        df = pd.read_csv(file)
    except Exception as e:
        raise ValueError(f"Could not parse file as CSV: {str(e)}")
        
    if df.empty:
        raise ValueError("The uploaded CSV file is empty.")
        
    # Standardize column names (strip whitespace)
    df.columns = [col.strip() for col in df.columns]
    
    return df
