import glob
import pandas as pd
import re
from IPython.display import clear_output, display
import random


def screen_exported_tables(
    root_path, sample_size=0.25, min_matching_percentage=0.5, sample=True, seed=-1
):
    """
    Screens CSV files in a given directory for columns that mostly match a specified pattern (Hospital numbers).

    Parameters:
    - root_path (str): Directory path containing the CSV files.
    - sample_size (float): The percentage of rows to sample from each file. Default is 0.25 (25%).
    - min_matching_percentage (float): Minimum percentage of matching values required to consider a column as mostly matching. Default is 0.5 (50%).
    - sample (bool): Whether to sample rows from the files or read the entire file. Default is True.
    - seed (int): Seed for random sampling reproducibility. Default is -1.
    """

    # Regular expression pattern to match a single character followed by six numbers
    pattern = re.compile(r"^[A-Z]\d{6}$")

    # Loop through each CSV file in the directory
    for file_path in glob.glob(root_path + "/*.csv"):
        # Read the CSV file with sampling or full reading
        if sample:
            # Count the number of lines in the file
            with open(file_path, "r") as file:
                total_lines = sum(1 for line in file)

            # Calculate the number of lines to sample, excluding the header
            lines_to_sample = int((total_lines - 1) * sample_size)

            # Randomly select line numbers to sample
            random.seed(seed)  # Set seed for reproducibility
            sample_lines = sorted(
                random.sample(range(1, total_lines), lines_to_sample)
            )  # Skip header (0)

            try:
                # Read the sampled lines into a DataFrame
                df = pd.read_csv(
                    file_path, skiprows=lambda i: i != 0 and i not in sample_lines
                )
            except Exception as e:
                print(f"Error reading sampled rows from {file_path}: {e}")
                continue
        else:
            try:
                # Read the entire CSV file
                df = pd.read_csv(file_path)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

        # Check each column for the pattern match
        pattern_match_found = False
        for column in df.columns:
            # Count the number of matching values in the column
            matching_count = (
                df[column].astype(str).apply(lambda x: bool(pattern.match(x))).sum()
            )

            # Calculate the percentage of matching values
            total_count = len(df[column])
            matching_percentage = matching_count / total_count if total_count > 0 else 0

            # Check if the percentage of matches is above the threshold
            if matching_percentage >= min_matching_percentage:
                print(
                    f"Column '{column}' in {file_path} mostly matches the pattern with {matching_percentage:.2%} matches."
                )
                pattern_match_found = True
                break

        if not pattern_match_found:
            print(f"No column in {file_path} mostly matches the pattern.")

        # Display the columns of the CSV file
        print(f"Columns of {file_path}:")
        print(df.columns)

        # Display the head of the CSV file
        print(f"Head of {file_path}:")
        display(df.head())

        # Wait for user input to proceed and then clear the output
        input("Press Enter to continue...")
        clear_output(wait=True)


# Example usage:
# screen_exported_tables('../_data/liverware/liverware_tables_export_datatype', sample_size=0.25, min_matching_percentage=0.5)
