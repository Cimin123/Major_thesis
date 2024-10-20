import pandas as pd
import pyperclip
import selenium as sel

def create_search_query(df, col, stop):
    query_string = ""
    counter = 0

    max_stop = min(stop, len(df) - 1)

    while counter <= max_stop:
        # Add each value to the query string, separated by a space (or other delimiter)
        query_string += f'"source:{str(df.iloc[counter][col])}" OR '
        counter += 1

    return query_string


articles_path = 'C:/Users/Admin/PycharmProjects/Major_thesis/InputData/Articles.csv'
articles_path_cols = ['Unikatowy Identyfikator Czasopisma', 'Tytuł 1', 'Tytuł 2', 'issn', 'Punktacja','302']
articles_categories = ['302']
titles_num = 10

articles_df = pd.read_csv(articles_path, usecols=articles_path_cols, skiprows=1)
articles_df_filtered = articles_df[articles_df[articles_categories].isin(['x']).any(axis=1)]
search_query = create_search_query(articles_df_filtered, 'Tytuł 1', titles_num)
pasted_string = pyperclip.copy(search_query)
print("String copied")
# ISSN Code for Poland is 57
