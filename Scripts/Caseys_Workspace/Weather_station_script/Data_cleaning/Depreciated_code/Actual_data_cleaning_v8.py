import pandas as pd
import os
import numpy as np
from datetime import datetime
import re

# Define conditions for identifying "bad data" in columns
bad_data_conditions = {
    'Swin_Avg (W/m²)': lambda x: x < 0 or pd.isna(x),
    'Thermocouple C': lambda x: pd.isna(x),
    'RH_Avg Percent': lambda x: x < 10 or x > 100,
    # Add other conditions if needed
}

# Function to extract date from filename
def extract_date_from_filename(file_name):
    date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', file_name)
    if date_match:
        month, day, year = date_match.groups()
        return pd.to_datetime(f"{year}-{month}-{day}", format="%Y-%m-%d")
    return None

# Function to identify "bad data" in "PT data" without altering the sheet
def identify_bad_data(pt_data, bad_data_conditions):
    bad_data_records = []

    for i in range(len(pt_data)):
        row = pt_data.iloc[i]
        bad_fields = [col for col, cond in bad_data_conditions.items() if col in pt_data.columns and cond(row[col])]

        if bad_fields:
            # Record bad data details for logging in the "Bad data" sheet
            bad_data_records.append({
                'Bad data Start': row['Date/Time'],
                'Bad data End': row['Date/Time'],
                'Data affected': ', '.join(bad_fields),
                'Notes': 'Bad data detected'
            })

    # Create "Bad data" DataFrame with the same headers as the original
    bad_data_df = pd.DataFrame(bad_data_records, columns=['Bad data Start', 'Bad data End', 'Data affected', 'Notes'])
    return bad_data_df

# Main function to process files based on date range and log "bad data"
def process_and_filter_bad_data(input_directory, start_date, end_date, output_file_base):
    all_bad_data_records = []
    combined_pt_data = []

    for root, dirs, files in os.walk(input_directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            extracted_date = extract_date_from_filename(file_name)

            # Check if the file is within the desired date range
            if extracted_date and start_date <= extracted_date <= end_date:
                xl = pd.ExcelFile(file_path)

                # Check for relevant sheets
                if 'PT data' in xl.sheet_names:
                    pt_data = xl.parse('PT data')
                    if not pt_data.empty:  # Ensure sheet is not empty
                        bad_data_new = identify_bad_data(pt_data, bad_data_conditions)
                        combined_pt_data.append(pt_data)  # Keep PT data unaltered
                        all_bad_data_records.append(bad_data_new)

    # Concatenate all PT data and bad data records
    pt_data_combined = pd.concat(combined_pt_data, ignore_index=True) if combined_pt_data else pd.DataFrame()
    bad_data_combined = pd.concat(all_bad_data_records, ignore_index=True) if all_bad_data_records else pd.DataFrame(columns=['Bad data Start', 'Bad data End', 'Data affected', 'Notes'])

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file_base), exist_ok=True)

    # Generate a unique output filename with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_file_base}_{timestamp}.xlsx"

    # Save to a new Excel file
    with pd.ExcelWriter(output_file, mode='w', engine='openpyxl') as writer:
        pt_data_combined.to_excel(writer, sheet_name='PT data', index=False)  # Original PT data
        bad_data_combined.to_excel(writer, sheet_name='Bad data', index=False)  # Identified bad data

    print(f"Original PT data and identified Bad data saved to {output_file}.")

# Script execution
if __name__ == "__main__":
    station_name = input("Enter the weather station name (e.g., 1311_Poloa): ")
    start_date_str = input("Enter the start date (YYYY-MM-DD): ")
    end_date_str = input("Enter the end date (YYYY-MM-DD): ")

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    input_directory = f'C:/Users/ctebe/OneDrive/Desktop/Wx/{station_name}'
    
    # Base output file path without timestamp
    output_file_base = (f'C:/Users/ctebe/OneDrive/Desktop/Wx/1.3.1.2 Aasu/Data/'
                        f'{station_name}_filtered_bad_data_{start_date.strftime("%Y-%m-%d")}_to_{end_date.strftime("%Y-%m-%d")}')

    process_and_filter_bad_data(input_directory, start_date, end_date, output_file_base)
