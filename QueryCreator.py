import pandas as pd
import pyperclip
import urllib


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
            query_string += f'source:"{str(self.filtered_df.iloc[counter][column_name])}" OR '

        return query_string.rstrip(" OR ")  # Remove the last " OR "

    # Create URL based on input
    def create_search_url(self, column_name):
        if self.filtered_df is None or column_name not in self.filtered_df.columns:
            print("Data not loaded or column not found.")
            return ""

        max_stop = min(self.max_titles, len(self.filtered_df) - 1)

        # Create the query string dynamically
        query_sources = [f'source:"{str(self.filtered_df.iloc[counter][column_name])}"' for counter in
                         range(max_stop + 1)]

        if not query_sources:
            print("No valid sources found.")
            return ""

        # Join query parts with OR
        query_string = " OR ".join(query_sources)
        encoded_query = urllib.parse.quote(query_string)

        # Construct the final Google Scholar URL
        base_url = "https://scholar.google.com/scholar?q="
        search_url = base_url + encoded_query

        return search_url


    # Copy search string to clipboard
    def copy_to_clipboard(self, query_string):
        pyperclip.copy(query_string)
        print("Query copied to clipboard.")


INPUT_PATH = "C:\\Users\\Szymon\\PycharmProjects\\Major_thesis\\InputData\\Articles.csv"
COLUMNS = ['Unikatowy Identyfikator Czasopisma', 'Tytuł 1', 'Tytuł 2', 'issn', 'Punktacja', '302']
CATEGORIES = ['302']  # ISSN Code for Poland is 57
MAX_TITLES = 10

query_creator = QueryCreator(INPUT_PATH, COLUMNS, CATEGORIES, MAX_TITLES)
query_creator.load_data()
search_query = query_creator.create_search_query('Tytuł 1')
search_url = query_creator.create_search_url('Tytuł 1')
if search_query:
    query_creator.copy_to_clipboard(search_url)