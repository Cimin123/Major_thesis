import os
import csv
import logging
import requests
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Google Scholar Search Query
BASE_URL = "https://scholar.google.com/scholar"
QUERY = "medical research"  # Change this to your desired search term
SEARCH_URL = f"{BASE_URL}?q={QUERY.replace(' ', '+')}&hl=en"

# User-defined variables
MAX_PUBS = 20  # Number of publications to process
DOWNLOAD_FOLDER = "pdf_downloads"
CSV_FILENAME = "publication_links.csv"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


PROXIES = [
    "http://195.154.255.118:80",
    "http://51.158.154.173:3128",
    "http://165.227.196.228:80",
    "http://178.62.193.19:3128",
    "http://46.4.96.137:1080",
]


def get_random_proxy():
    """Returns a random proxy from the list."""
    return {"http": random.choice(PROXIES), "https": random.choice(PROXIES)}


def get_publication_proxies_links(max_pubs):
    logging.info("Fetching publication links with proxy...")

    # Get fresh proxies
    proxies = get_free_proxies()
    if not proxies:
        logging.error("No proxies available. Exiting.")
        return []

    links = []
    retries = 5  # Maximum retries with different proxies

    while retries > 0 and len(links) < max_pubs:
        proxy = get_random_proxy(proxies)
        if not proxy:
            break

        logging.info(f"Using proxy: {proxy}")

        try:
            response = requests.get(SEARCH_URL, headers=HEADERS, proxies=proxy, timeout=10)
            if response.status_code != 200:
                logging.warning(f"Proxy blocked or request failed. Status Code: {response.status_code}")
                retries -= 1
                continue  # Try a new proxy

            soup = BeautifulSoup(response.text, "html.parser")

            for entry in soup.select('.gs_r a[href]'):
                href = entry['href']

                # Filter out Google Scholar internal links
                if "scholar.google.com" in href:
                    continue

                full_url = urljoin(BASE_URL, href)

                # Check if it's a direct PDF link
                if href.endswith(".pdf"):
                    logging.info(f"Found PDF: {full_url}")
                    links.append(full_url)
                else:
                    links.append(full_url)

                # Stop when max publications reached
                if len(links) >= max_pubs:
                    break

            logging.info(f"Found {len(links)} publication links.")
            return links

        except requests.exceptions.RequestException as e:
            logging.error(f"Proxy request failed: {e}")
            retries -= 1  # Retry with a new proxy

    logging.error("All proxies failed. Try again later.")
    return []


# Function to get publication links from search results
def get_publication_links(max_pubs):
    logging.info("Fetching publication links...")
    response = requests.get(SEARCH_URL, headers=HEADERS)
    if response.status_code != 200:
        logging.error(f"Failed to retrieve Google Scholar page. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for entry in soup.select('.gs_or_ggsm a[href]'):
        href = entry['href']

        # Filter out internal Google Scholar links
        if "scholar.google.com" in href:
            continue

        full_url = urljoin(BASE_URL, href)

        links.append(full_url)
        # Check if it's a direct PDF link
        # if href.endswith(".pdf"):
        #     logging.info(f"Found PDF: {full_url}")
        #     links.append(full_url)
        # else:
        #     links.append(full_url)

        # Stop when we reach max publications
        if len(links) >= max_pubs:
            break

    logging.info(f"Found {len(links)} publication links.")
    return links


def get_many_publication_links(query, max_pubs, max_pages):
    logging.info("Fetching publication links...")
    links = []

    for page in range(max_pages):
        start = page * 10  # Each Scholar page has 10 results
        params = {"q": query, "start": start}

        response = requests.get(SEARCH_URL, headers=HEADERS, params=params)
        if response.status_code != 200:
            logging.error(f"Failed to retrieve Google Scholar page {page + 1}. Status Code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        for entry in soup.select('.gs_or_ggsm a[href]'):
            href = entry['href']

            # Filter out internal Google Scholar links
            if "scholar.google.com" in href:
                continue

            full_url = urljoin(BASE_URL, href)
            links.append(full_url)

            # Stop when we reach max publications
            if len(links) >= max_pubs:
                logging.info(f"Reached max publications: {len(links)}")
                return links

    logging.info(f"Found {len(links)} publication links.")
    return links



# Function to save publication links to a CSV file
def save_links_to_csv(links, filename):
    logging.info(f"Saving links to {filename}...")
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Publication URL"])
        for link in links:
            writer.writerow([link])
    logging.info("Links saved successfully.")


# Function to extract and download PDFs from publication pages
def download_pdfs_from_links(publication_links):
    for index, link in enumerate(publication_links, start=1):
        logging.info(f"[{index}/{len(publication_links)}] Visiting publication page: {link}")
        try:
            response = requests.get(link, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                logging.warning(f"Could not access {link}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.pdf')]

            if pdf_links:
                for pdf_link in pdf_links:
                    download_pdf(pdf_link)
            else:
                logging.info("No PDFs found on this page.")

        except requests.RequestException as e:
            logging.error(f"Error accessing {link}: {e}")


# Function to download a PDF
def download_pdf(pdf_url):
    filename = os.path.join(DOWNLOAD_FOLDER, pdf_url.split("/")[-1])

    try:
        response = requests.get(pdf_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        with open(filename, "wb") as file:
            file.write(response.content)
        logging.info(f"Downloaded: {filename}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download {pdf_url}: {e}")


# Main Execution
if __name__ == "__main__":
    #publication_links = get_publication_links(MAX_PUBS)
    query = "medicine"
    publication_links = get_many_publication_links(query, 40, 3)
    print(publication_links)
    save_links_to_csv(publication_links, CSV_FILENAME)
    #pdf = "https://folk.ntnu.no/slyderse/medstat/st2303/Armitage%20et%20al%20Multilevel.pdf"
    for link in publication_links:
        try:
            download_pdf(link)
        except:
            print("Coulndt download")
