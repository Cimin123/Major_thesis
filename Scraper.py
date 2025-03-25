import os
import csv
import logging
import requests
import re
import random
import time
from bs4 import BeautifulSoup

from urllib.parse import urljoin


# Google Scholar scraper
class Scraper:
    HEADERS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0"
    ]

    def __init__(self, url, query, max_pubs=20, proxies_file=None, output_folder="PDFDownloads",
                 csv_filename="publication_links.csv"):
        self.url = url
        self.query = query
        self.max_pubs = max_pubs
        self.max_pages = max_pubs // 10
        self.pubs_per_page = 10
        self.output_folder = output_folder
        self.csv_filename = csv_filename
        self.proxies = self.load_proxies(proxies_file) if proxies_file else []
        self.session = requests.Session()

        os.makedirs(self.output_folder, exist_ok=True)

        # Configure logging
        logging.basicConfig(level=logging.INFO)

    # Loads proxies from .txt file
    @staticmethod
    def load_proxies(proxies_file):
        try:
            with open(proxies_file, "r") as f:
                proxies = {line.strip(): True for line in f.readlines()}
            logging.info(f"Loaded {len(proxies)} proxies.")
            return proxies
        except Exception as e:
            logging.error(f"Error loading proxies: {e}")
            return {}

    # Add random delay
    @staticmethod
    def random_delay(min_delay=10, max_delay=30):
        delay = random.uniform(min_delay, max_delay)  # Generate random float between min and max
        time.sleep(delay)

    # Proxy rotation
    def get_random_proxy(self):
        if not self.proxies:
            return None

        # Filter for valid proxies
        valid_proxies = [proxy for proxy, is_valid in self.proxies.items() if is_valid]

        proxy = random.choice(valid_proxies)
        return proxy

    def out_of_proxy(self):
        return not any(is_valid for is_valid in self.proxies.values())

    # Get all publications from given page
    def get_publication_links(self):
        logging.info(f"Fetching publication links for query: {self.query}")
        links = []

        for page in range(self.max_pages):
            page_scrapped = False
            start = page * self.pubs_per_page  # Each Scholar page contains 10 results
            params = {"as_vs": 1, "hl": "pl", "q": self.query, "as_sdt": "0%2C5", "start": start}

            # Look for working proxy until page is scrapped
            while not page_scrapped and self.out_of_proxy():
                try:
                    proxy = self.get_random_proxy()
                    header_agent = {"User-Agent": random.choice(self.HEADERS)}

                    full_url = requests.Request("GET", self.url, params=params).prepare().url
                    print(f'Proxy: {proxy} header {header_agent} url {full_url}')
                    response = requests.get(self.url, headers=header_agent, params=params, proxies=proxy, timeout=10)

                    if response.status_code != 200:
                        print(f"Failed to retrieve page {page + 1}. Status Code: {response.status_code}")
                        self.proxies[proxy] = False

                        continue

                    else:
                        print(f'Proxy: {proxy} is working correctly!. Page {page} scraped')

                    soup = BeautifulSoup(response.text, "html.parser")

                    for entry in soup.select('.gs_or_ggsm a[href]'):
                        href = entry['href']
                        if "scholar.google.com" in href:  # Ignore internal Google Scholar links
                            continue

                        full_url = urljoin(self.url, href)
                        links.append(full_url)

                        if len(links) >= self.max_pubs:
                            logging.info(f"Reached max publications: {len(links)}")
                            return links

                    page_scrapped = True

                except requests.RequestException as e:
                    logging.error(f"Error fetching Google Scholar results: {e}")

                self.random_delay()

        logging.info(f"Total links found: {len(links)}")
        print(links, sep="\n")
        return links

    # Save scrapped links to csv
    def save_links_to_csv(self, links):
        logging.info(f"Saving {len(links)} links to {self.csv_filename}...")
        with open(self.csv_filename, mode="a", newline="", encoding="utf-8") as file:
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

    @staticmethod
    def sanitize_filename(url):
        # Get the last part of the path or fallback to full base64
        filename = url.split("/")[-1].split("?")[0]
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        # Remove or replace characters invalid in filenames
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return filename

    # Function for downloading PDFs
    def download_pdf(self, pdf_url):
        filename = self.sanitize_filename(pdf_url)
        filepath = os.path.join(self.output_folder, filename)
        header_agent = {"User-Agent": random.choice(self.HEADERS)}

        try:
            response = requests.get(pdf_url, headers=header_agent, timeout=10)
            response.raise_for_status()
            with open(filepath, "wb") as file:
                file.write(response.content)
            logging.info(f"Downloaded: {filename}")

        except requests.RequestException as e:
            logging.error(f"Failed to download {pdf_url}: {e}")
