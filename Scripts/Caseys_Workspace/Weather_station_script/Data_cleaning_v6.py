import pandas as pd
import os
import logging

# Setup logging
logging.basicConfig(
    filename='data_processing.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def clean_weather_data(file_path):
    try:
        print(f"Processing file: {file_path}")  # Add this print statement for debugging
        df = pd.read_excel(file_path, skiprows=3)
        print(f"File shape: {df.shape}")  # Check the dimensions of the DataFrame
        new_header_mapping = {
            'Unnamed: 0': 'Date/Time',
            'Avg': 'Swin_Avg (W/m²)',
            'Avg.1': 'Thermocouple C',
            'Smp': 'RH_Avg Percent',
            'Avg.2': 'VP_Avg (kPa)',
            'Avg.3': 'VPsat_Avg (kPa)',
            'Avg.4': 'VPD_Avg (kPa)',
            'Smp.1': 'WS_Avg (m/s)',
            'Smp.2': 'WSrs_Avg (m/s)',
            'Smp.3': 'WDuv_Avg (degrees)',
            'Smp.4': 'WDrs_Avg (degrees)',
            'Smp.5': 'WD_StdY (degrees)',
            'Smp.6': 'WD_StdCS (degrees)',
            'Tot': 'RF_Tot (mm)'
        }

        df_cleaned = df.rename(columns=new_header_mapping)
        df_cleaned = df_cleaned.drop(columns=['Unnamed: 1'], errors='ignore')
        
        print(f"Finished processing: {file_path}")  # Add this
        return df_cleaned

    except Exception as e:
        logging.error(f"Failed to process file {file_path}: {e}")
        print(f"Error processing {file_path}: {e}")  # Add this
        return None

def process_multiple_files_to_single_sheet(input_dir, output_file):
    print(f"Processing files in directory: {input_dir}")  # Add this print statement
    combined_df = pd.DataFrame()  # Initialize an empty DataFrame

    for filename in os.listdir(input_dir):
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(input_dir, filename)
            df_cleaned = clean_weather_data(file_path)

            if df_cleaned is not None and not df_cleaned.empty:  # Ensure the dataframe is not empty
                combined_df = pd.concat([combined_df, df_cleaned], ignore_index=True)
                logging.info(f"Successfully processed: {file_path}")

    if combined_df.empty:
        print("No data was processed.")  # Add this line if no data was added
    else:
        combined_df.to_excel(output_file, index=False)
        logging.info(f"All files processed and saved into {output_file}")
        print(f"All files processed and saved into {output_file}")  # Add this

# Example usage
input_directory = r'C:\Users\ctebe\OneDrive\Desktop\GitHub Repositories\Hydro_Monitoring_Network_ASPA-UH\Final_Historical_Data\Weather_Stations'
output_file = r'C:\Users\ctebe\OneDrive\Desktop\GitHub Repositories\Hydro_Monitoring_Network_ASPA-UH\Final_Historical_Data\combined_output_single_sheet.xlsx'

process_multiple_files_to_single_sheet(input_directory, output_file)