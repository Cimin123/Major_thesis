import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


class Scrapper:
    def __init__(self):
        self.driver = self.configure_driver()
        self.links = []

    def configure_driver(self):
        chrome_driver_path = "./chromedriver.exe"  # Update with your correct path

        service = Service(executable_path=chrome_driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # For headless browsing
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def dismiss_cookie_message(self):
        try:
            # Update the selector to match the cookie consent button on your webpage
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button#onetrust-accept-btn-handler"))
            ).click()
            print("Cookie consent message dismissed.")
        except TimeoutException:
            print("TimeoutException: Cookie consent message not found or could not be dismissed")

    def get_links_from_page(self, url):
        self.driver.get(url)

        # Dismiss the cookie consent message if it exists
        self.dismiss_cookie_message()

        try:
            # Wait for the div with class 'szukaj-bloczki__content' to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "szukaj-bloczki__content"))
            )
            print("Element 'szukaj-bloczki__content' found")
        except TimeoutException:
            print("TimeoutException: Element 'szukaj-bloczki__content' not found")
            return None

        # If the element is found, continue with parsing
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        for div in soup.find_all("div", class_="szukaj-bloczki__content"):
            for a in div.find_all("a", href=True):
                self.links.append(a['href'])
                print(f"Found link: {a['href']}")  # Print for debugging

    def scrape_pages(self, base_url, total_pages):
        for page in range(1, total_pages + 1):
            url = base_url.replace("&strona=1", f"&strona={page}")
            print(f"Scraping page {page}: {url}")
            self.get_links_from_page(url)

    def save_links_to_csv(self, filename):
        base_url = "https://r.pl"
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["URL"])
            for link in self.links:
                full_url = base_url + link if not link.startswith(base_url) else link
                writer.writerow([full_url])
        print(f"Links saved to {filename}")

    def close_driver(self):
        self.driver.quit()


# Example usage within the class file for testing
if __name__ == "__main__":
    base_url = "https://r.pl/szukaj?typTransportu=AIR&data&dorosli=1994-01-01&dorosli=1994-01-01&dorosli=1994-01-01&dzieci=nie&liczbaPokoi=1&dowolnaLiczbaPokoi=nie&dataWylotu&dlugoscPobytu=*-*&dlugoscPobytu.od=&dlugoscPobytu.do=&cena=avg&cena.od=&cena.do=&ocenaKlientow=*-*&odlegloscLotnisko=*-*&hotelUrl&produktUrl&sortowanie=cena-asc&strona=1"
    scrapper = Scrapper()
    scrapper.scrape_pages(base_url, 20)
    scrapper.save_links_to_csv("links.csv")
    scrapper.close_driver()
