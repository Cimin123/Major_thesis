import os
import csv
import logging
import requests
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# Google Scholar scraper
class Scraper:
    BASE_URL = "https://scholar.google.com/scholar"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def __init__(self, query, max_pubs=20, proxies_file=None, output_folder="PDFDownloads",
                 csv_filename="publication_links.csv"):
        self.query = query
        self.max_pubs = max_pubs
        self.max_pages = max_pubs // 10
        self.output_folder = output_folder
        self.csv_filename = csv_filename
        self.proxies = self.load_proxies(proxies_file) if proxies_file else []
        os.makedirs(self.output_folder, exist_ok=True)

        # Configure logging
        logging.basicConfig(level=logging.INFO)

    # Loads proxies from .txt file
    def load_proxies(self, proxies_file):
        try:
            with open(proxies_file, "r") as f:
                proxies = [line.strip() for line in f.readlines()]
            logging.info(f"Loaded {len(proxies)} proxies.")
            return proxies
        except Exception as e:
            logging.error(f"Error loading proxies: {e}")
            return []

    # Proxy rotation
    def get_random_proxy(self):
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return {"http": proxy, "https": proxy}

    # Get all publications from given page
    def get_publication_links(self):
        logging.info(f"Fetching publication links for query: {self.query}")
        links = []

        for page in range(self.max_pages):
            start = page * 10  # Each Scholar page contains 10 results
            params = {"q": self.query, "start": start}

            try:
                proxy = self.get_random_proxy()
                response = requests.get(self.BASE_URL, headers=self.HEADERS, params=params, proxies=proxy, timeout=10)

                if response.status_code != 200:
                    logging.error(f"Failed to retrieve page {page + 1}. Status Code: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

                for entry in soup.select('.gs_or_ggsm a[href]'):
                    href = entry['href']
                    if "scholar.google.com" in href:  # Ignore internal Google Scholar links
                        continue

                    full_url = urljoin(self.BASE_URL, href)
                    links.append(full_url)

                    if len(links) >= self.max_pubs:
                        logging.info(f"Reached max publications: {len(links)}")
                        return links

            except requests.RequestException as e:
                logging.error(f"Error fetching Google Scholar results: {e}")

        logging.info(f"Total links found: {len(links)}")
        return links

    # Save scrapped links to csv
    def save_links_to_csv(self, links):
        logging.info(f"Saving {len(links)} links to {self.csv_filename}...")
        with open(self.csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Publication URL"])
            for link in links:
                writer.writerow([link])
        logging.info("Links saved successfully.")

    # Extract pdf links from Scholar
    def download_pdf_links(self, publication_links):
        for index, link in enumerate(publication_links, start=1):
            logging.info(f"[{index}/{len(publication_links)}] Visiting publication page: {link}")
            try:
                response = requests.get(link, headers=self.HEADERS, timeout=10)
                if response.status_code != 200:
                    logging.warning(f"Could not access {link}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.pdf')]

                if pdf_links:
                    for pdf_link in pdf_links:
                        self.download_pdf(pdf_link)
                else:
                    logging.info("No PDFs found on this page.")

            except requests.RequestException as e:
                logging.error(f"Error accessing {link}: {e}")

    # Function for downloading PDFs
    def download_pdf(self, pdf_url):
        filename = os.path.join(self.output_folder, pdf_url.split("/")[-1])

        try:
            response = requests.get(pdf_url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            with open(filename, "wb") as file:
                file.write(response.content)
            logging.info(f"Downloaded: {filename}")
        except requests.RequestException as e:
            logging.error(f"Failed to download {pdf_url}: {e}")
