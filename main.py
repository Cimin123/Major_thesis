import argparse
import logging
import pandas as pd
from Scraper import Scraper


def load_proxies(proxy_file):
    """Loads proxies from a file, one per line."""
    try:
        with open(proxy_file, "r") as f:
            proxies = [line.strip() for line in f.readlines()]
        logging.info(f"Loaded {len(proxies)} proxies.")
        return proxies
    except Exception as e:
        logging.error(f"Error loading proxies: {e}")
        return []


def load_categories(input_csv, category_col):
    """Loads and filters data based on a category column from a CSV file."""
    try:
        df = pd.read_csv(input_csv)
        if category_col not in df.columns:
            logging.error(f"Column '{category_col}' not found in CSV.")
            return []

        filtered_df = df[df[category_col].notna()]
        return filtered_df
    except Exception as e:
        logging.error(f"Error loading CSV: {e}")
        return []

# python main.py "https://scholar.google.com/scholar?hl=pl&as_sdt=0%2C5&q=radiologia&btnG=" "20" "valid_proxies.txt"
def main():
    parser = argparse.ArgumentParser(description="Google Scholar Scraper")

    parser.add_argument("query", type=str, help="Search query for Google Scholar")
    #parser.add_argument("input_csv", type=str, help="Path to input CSV file with categories")
    #parser.add_argument("category_col", type=str, help="Column name containing categories to filter")
    parser.add_argument("max_pages", type=int, help="Number of pages to scrape")
    parser.add_argument("proxy_file", type=str, help="Path to proxy file")

    args = parser.parse_args()

    # Load proxies and filtered data
    proxies = load_proxies(args.proxy_file)
    #filtered_data = load_categories(args.input_csv, args.category_col)

    # if filtered_data.empty:
    #     logging.error("No data found for the specified category.")
    #     return

    # Start the scraper
    scraper = Scraper(
        query=args.query,
        max_pubs=100,
        proxies_file=args.proxy_file
    )

    if proxies:
        scraper.PROXIES = proxies

    publication_links = scraper.get_publication_links()
    scraper.save_links_to_csv(publication_links)

    # Download PDFs
    for link in publication_links:
        try:
            scraper.download_pdf(link)
        except Exception as e:
            logging.error(f"Couldn't download {link}: {e}")


if __name__ == "__main__":
    main()

