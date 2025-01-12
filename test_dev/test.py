import pandas as pd


def detect_data_type(series):
    """
    Detect the data type of a pandas Series.
    """
    try:
        pd.to_numeric(series.dropna(), errors='raise')
        return 'integer' if all(series.dropna().astype(str).str.isnumeric()) else 'floating'
    except ValueError:
        return 'string'


def print_overview(df):
    """
    Print an overview of the dataset, including missing values and possible unique columns.
    """
    print("\n--- Data Overview ---")
    print(f"Total rows: {df.shape[0]}")
    print(f"Total columns: {df.shape[1]}")

    # Missing values overview
    print("\nMissing values per column:")
    missing_counts = df.isna().sum()
    if missing_counts.any():
        for column, missing_count in missing_counts.items():
            if missing_count > 0:
                detected_type = detect_data_type(df[column])
                print(f" - {column}: {missing_count} missing values (Detected type: {detected_type})")
    else:
        print("No missing values.")

    # Possible unique columns
    print("\nPossible unique columns:")
    for column in df.columns:
        unique_values = df[column].nunique(dropna=True)
        total_values = len(df[column].dropna())
        missing_count = df[column].isna().sum()
        if unique_values == total_values and missing_count == 0:
            print(f" - {column} (Unique: Yes)")
        else:
            print(f" - {column} (Unique: No)")


def validate_column(column_name, series):
    """
    Validate a single column for missing values, data type mismatches, and potential uniqueness.
    """
    print(f"\n--- Validating column '{column_name}' ---")

    # Detect data type
    detected_type = detect_data_type(series)
    print(f" - Detected data type: {detected_type}")

    # Check for missing values
    missing_count = series.isna().sum()
    if missing_count > 0:
        print(f" - Missing values detected: {missing_count}")
    else:
        print(" - No missing values detected.")

    # Check for wrong data type
    invalid_data_count = series.dropna().apply(
        lambda x: isinstance(x, (int, float) if detected_type in ['integer', 'floating'] else str)
    ).sum()
    if invalid_data_count < len(series.dropna()):
        print(f" - Data type mismatch: {len(series.dropna()) - invalid_data_count} rows.")
    else:
        print(" - All rows have correct data type.")

    # Check if the column has potential to be unique
    unique_values = series.nunique(dropna=True)
    total_values = len(series.dropna())
    if unique_values == total_values and missing_count == 0:
        print(" - This column can be a unique column.")
    else:
        print(" - This column cannot be a unique column.")
        print(f"   Unique values: {unique_values}, Total non-missing values: {total_values}")


def validate_csv(file_path):
    """
    Validate a CSV file column by column, with an overview.
    """
    try:
        # Load data from CSV
        df = pd.read_csv(file_path)
        print(f"Loaded data with {df.shape[0]} rows and {df.shape[1]} columns.")

        # Print overview
        print_overview(df)

        # Validate each column
        for column in df.columns:
            validate_column(column, df[column])

    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    file_path = "test_missing.csv"  # Replace with your CSV file path
    validate_csv(file_path)
