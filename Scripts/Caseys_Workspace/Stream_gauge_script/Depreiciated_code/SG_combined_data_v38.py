import os
import pandas as pd
import logging
import re
from openpyxl import load_workbook

# Setup logging to both console and file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("data_processing.log"),
    logging.StreamHandler()
])

# List of filenames to ignore
ignore_files = [
    'Nuuuli_4.1.1-2020.12.18.csv', 'Nuuuli_4.1.1-2022.1.6.csv',
    'Nuuuli_4.1.1-2022.10.19.csv', 'Nuuuli_4.1.1-2022.11.17.csv',
    'Nuuuli_4.1.1-2022.12.14.csv', 'Nuuuli_4.1.1-2022.2.8.csv',
    'Nuuuli_4.1.1-2022.4.22.csv', 'Nuuuli_4.1.1-2022.5.16.csv',
    'Nuuuli_4.1.1-2022.6.16.csv', 'Nuuuli_4.1.1-2022.7.15.csv',
    'Nuuuli_4.1.1-2022.8.15.csv', 'Nuuuli_4.1.1-2022.9.15.csv',
    'Nuuuli_4.1.1-2023.1.17.csv', 'Nuuuli_4.1.1-2023.10.16.csv',
    'Nuuuli_4.1.1-2023.12.15.csv', 'Nuuuli_4.1.1-2023.2.15.csv',
    'Nuuuli_4.1.1-2023.3.17.csv', 'Nuuuli_4.1.1-2023.4.14.csv',
    'Nuuuli_4.1.1-2023.5.15.csv', 'Nuuuli_4.1.1-2023.6.15.csv',
    'Nuuuli_4.1.1-2023.7.14.csv', 'Nuuuli_4.1.1-2023.8.16.csv',
    'Nuuuli_4.1.1-2023.9.15.csv', 'Nuuuli_ALL_SG_data.xlsx'
]

# Standard headers and mapping for column alignment
standard_headers = [
    'Date/Time', 'WTlvl_Avg', 'Twt_F_Avg', 'BattVolt_Avg',
    'BattVolt_Min', 'Tpanel_Avg', 'TCair_Avg', 'RHenc', 'RF_Tot (mm)'
]

header_mapping = {
    'Date Time, GMT-11:00': 'Date/Time',
    'Abs Pres, psi': 'WTlvl_Avg',
    'Temp, °F': 'Twt_F_Avg',
    'Batt_Volt_Avg': 'BattVolt_Avg',
    'Batt_Volt_Min': 'BattVolt_Min',
    'Panel_Temp': 'Tpanel_Avg',
    'Air_Temp_C': 'TCair_Avg',
    'Rel_Humidity': 'RHenc',
    'Rain_Total_mm': 'RF_Tot (mm)',
    # Add any other mappings needed
}

# Date extraction from filename using regex
def extract_date_from_filename(file_name):
    try:
        date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', file_name)
        if date_match:
            month, day, year = date_match.groups()
            extracted_date = pd.to_datetime(f"{year}-{month}-{day}", format="%Y-%m-%d")
            logging.info(f"Extracted date {extracted_date} from file: {file_name}")
            return extracted_date
    except Exception as e:
        logging.error(f"Failed to extract date from filename {file_name}: {e}")
    return None

# Function to map columns based on header_mapping
def map_columns(df):
    logging.info(f"Mapping columns for file with headers: {df.columns.tolist()}")
    
    # Apply the column mapping
    df = df.rename(columns=header_mapping)
    
    # Ensure no duplicated columns
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Ensure all standard headers are present, add missing columns
    for header in standard_headers:
        if header not in df.columns:
            df[header] = None
    
    logging.info(f"Final mapped columns: {df.columns.tolist()}")
    return df

# Function to clean CSV files
def clean_csv_data(file_path):
    logging.info(f"Processing CSV file: {file_path}")
    df = pd.read_csv(file_path)
    df = map_columns(df)
    return df

# Function to clean Excel files
def clean_xlsx_data(file_path):
    logging.info(f"Processing XLSX file: {file_path}")
    xl = pd.ExcelFile(file_path)
    logging.info(f"Available sheets: {xl.sheet_names}")
    
    # Look for 'PT data', else fallback to the first non-empty sheet
    if 'PT data' in xl.sheet_names:
        df = xl.parse('PT data')
    else:
        for sheet in xl.sheet_names:
            df = xl.parse(sheet)
            if not df.empty:
                logging.info(f"Using sheet: {sheet}")
                break
    
    df = map_columns(df)
    return df

# Function to process files based on type
def process_file(file_path):
    logging.info(f"Processing file: {file_path}")
    if file_path.endswith('.csv'):
        df = clean_csv_data(file_path)
    elif file_path.endswith('.xlsx'):
        df = clean_xlsx_data(file_path)
    else:
        logging.warning(f"Unsupported file format: {file_path}")
        return None
    
    if df is not None:
        df = df.reset_index(drop=True)
    return df

# Function to combine and clean data for the specified station
def process_multiple_files_to_single_sheet(input_directory, output_file, start_date, end_date):
    all_data = []
    logging.info("Starting the script.")
    print("Starting the script...")

    # Walk through directory and process files
    for root, dirs, files in os.walk(input_directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # Skip files that are in the ignore list
            if file_name in ignore_files:
                logging.info(f"Skipping ignored file: {file_name}")
                print(f"Skipping ignored file: {file_name}")
                continue

            if file_name.endswith('.csv') or file_name.endswith('.xlsx'):
                extracted_date = extract_date_from_filename(file_name)
                if extracted_date and start_date <= extracted_date <= end_date:
                    df_cleaned = process_file(file_path)
                    if df_cleaned is not None:
                        all_data.append(df_cleaned)

    # Combine and save data if available
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        logging.info(f"Saving data to {output_file}")
        combined_df.to_excel(output_file, index=False, engine='openpyxl')
        logging.info(f"Data successfully saved to {output_file}")
        print(f"Data saved to: {output_file}")
        print("Final combined data preview:")
        print(combined_df.head())
    else:
        logging.info("No valid data found.")
        print("No valid data found.")

    print("Script completed.")

# Example usage
# input_directory = "path_to_your_input_directory"
# output_file = "path_to_output.xlsx"
# start_date = pd.to_datetime("YYYY-MM-DD")
# end_date = pd.to_datetime("YYYY-MM-DD")
# process_multiple_files_to_single_sheet(input_directory, output_file, start_date, end_date)