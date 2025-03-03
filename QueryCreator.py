import pandas as pd
import pyperclip


# Class responsible for handling search strings
class QueryCreator:
    def __init__(self, file_path, columns, categories, max_titles):
        self.file_path = file_path
        self.columns = columns
        self.categories = categories
        self.max_titles = max_titles
        self.df = None
        self.filtered_df = None

    # Load desired columns from input excel
    def load_data(self):
        try:
            self.df = pd.read_csv(self.file_path, usecols=self.columns, skiprows=1)
            self.filtered_df = self.df[self.df[self.categories].isin(['x']).any(axis=1)]
        except Exception as e:
            print(f"Error loading data: {e}")

    # Create scholar search string
    def create_search_query(self, column_name):
        if self.filtered_df is None or column_name not in self.filtered_df.columns:
            print("Data not loaded or column not found.")
            return ""

        query_string = ""
        max_stop = min(self.max_titles, len(self.filtered_df) - 1)

        for counter in range(max_stop + 1):
            query_string += f'"source:{str(self.filtered_df.iloc[counter][column_name])}" OR '

        return query_string.rstrip(" OR ")  # Remove the last " OR "

    # Copy search string to clipboard
    def copy_to_clipboard(self, query_string):
        pyperclip.copy(query_string)
        print("Query copied to clipboard.")