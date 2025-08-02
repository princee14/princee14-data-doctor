import pandas as pd

def clean_data(df, remove_outliers=True):
    cleaning_summary = []

    original_shape = df.shape

    # 1. Remove duplicates
    df = df.drop_duplicates()
    cleaning_summary.append(f"Removed {original_shape[0] - df.shape[0]} duplicate rows.")

    # 2. Handle missing values
    num_missing_before = df.isnull().sum().sum()
    for col in df.columns:
        if df[col].dtype == 'O':  # Object (categorical/string)
            mode_val = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
            df[col] = df[col].fillna(mode_val)
        else:  # Numeric
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
    num_missing_after = df.isnull().sum().sum()
    cleaned_missing = num_missing_before - num_missing_after
    cleaning_summary.append(f"Filled {cleaned_missing} missing values.")

    # 3. Convert only likely date columns
    date_cols = []
    for col in df.columns:
        # only attempt conversion if column name suggests it is a date
        if any(keyword in col.lower() for keyword in ["date", "dob", "time", "join", "start", "end"]):
            try:
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors='raise')
                date_cols.append(col)
            except:
                continue
    if date_cols:
        cleaning_summary.append(f"Converted columns to datetime: {', '.join(date_cols)}")

    # 4. Remove outliers
    if remove_outliers:
        numeric_cols = df.select_dtypes(include='number').columns
        before_rows = df.shape[0]
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df = df[(df[col] >= lower) & (df[col] <= upper)]
        after_rows = df.shape[0]
        removed_outliers = before_rows - after_rows
        cleaning_summary.append(f"Removed {removed_outliers} outlier rows.")

    return df, cleaning_summary
