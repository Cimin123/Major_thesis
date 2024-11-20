import csv
import logging
import bs4
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import time
from datetime import datetime

logging.getLogger('selenium').setLevel(logging.CRITICAL)

class LinkVisitor:
    def __init__(self, csv_filename):
        self.file_num = 60
        self.list_start = 32
        self.list_end = 40
        self.csv_filename = csv_filename
        #self.driver = self.configure_driver()
        #self.links = self.read_links_from_csv()
        self.publication_links = []

    def configure_driver(self):
        chrome_driver_path = "./chromedriver.exe"  # Update with your correct path

        service = Service(executable_path=chrome_driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # For headless browsing
        options.add_argument('--log-level=3')  # Suppress logging
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def get_soup_from_url(url):
        try:
            # Make an HTTP GET request to the specified URL
            response = requests.get(url)
            # Raise an exception if the request was not successful (status code != 200)
            response.raise_for_status()
            # Parse the HTML content with BeautifulSoup
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            return soup
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def extract_links_from_divs(soup):

        # Find all divs with class "gs" or "ggsm"
        target_divs = soup.find_all('div', class_=['gs_or_ggsm'])

        links = []
        # Iterate through each found div and extract <a> tags
        for div in target_divs:
            a_tags = div.find_all('a', href=True)
            for a_tag in a_tags:
                span_tag = a_tag.find('span')
                if span_tag and '[PDF]' in span_tag.text:
                    links.append(a_tag['href'])
        return links

    def click_button_for_links(links, driver):
        """
        Visits each link and simulates clicking the button with the class "crv_icon" using Selenium.

        Args:
        - links (list): A list of URLs to visit.

        Returns:
        - list: A list of URLs extracted from buttons with the class "crv_icon".
        """
        # Set up the Selenium WebDriver (using Chrome)
        #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        button_links = []

        for link in links:
            try:
                # Navigate to the specified URL
                driver.get(link)
                time.sleep(2)  # Wait for the page to load

                # Find the button with class "crv_icon" or the <cr-icon-button>
                try:
                    button = driver.find_element(By.CLASS_NAME, 'crv_icon')
                except:
                    button = None

                if not button:
                    try:
                        button = driver.find_element(By.ID, 'download')
                    except:
                        button = None
            except Exception as e:
                print(f"An error occurred while processing link {link}: {e}")

        driver.quit()
        return button_links

    def click_button_if_present(self, class_):
        try:
            button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, class_))
            )
            button.click()
            print("Button clicked.")
            return True
        except (TimeoutException, NoSuchElementException):
            print("Button not found or not clickable.")
            return False

    def read_links_from_csv(self):
        base_url = "https://r.pl"
        links = []
        with open(self.csv_filename, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for index, row in enumerate(reader):
                if index < self.file_num:  # Read only the first 5 positions
                    links.append(base_url + row[0])
                else:
                    break
        print(f"Read {len(links)} links from {self.csv_filename}")
        return links

    def extract_header_text(self):
        try:
            header = self.driver.find_element(By.CSS_SELECTOR,
                                              "h1.r-typography.r-typography--main.r-typography--bold.r-typography--black.r-typography__h1.r-typography--break-word.kh-header__title")
            return header.text
        except NoSuchElementException:
            return None

    def visit_links(self):
        self.links = self.links[self.list_start:self.list_end]
        for link in self.links:
            print(f"Visiting: {link}")
            self.driver.get(link)
            try:
                # Click the button if it exists
                self.click_button_if_present("button.r-button.r-button--accent.r-button--hover.r-button--contained.r-button--only-text.r-button--svg-margin-left.r-consent-buttons__button.cmpboxbtnyes")
                self.click_button_if_present("button.r-button.r-button--uppercase.r-button--accent.r-button--hover.r-button--contained.r-button--only-text.r-button--svg-margin-left")

                if(self.click_button_if_present("button.r-button.r-button--primary.r-button--text.r-button--only-text.r-button--svg-margin-left.kh-konfigurator-skad__rozklad")):
                    self.extract_flights_departure_data()
                    self.extract_flights_arrival_data()
                else:
                    self.dateDeparture.append(None)
                    self.timeDeparture.append(None)
                    self.cityDeparture.append(None)
                    self.dateArrival.append(None)
                    self.timeArrival.append(None)
                    self.cityArrival.append(None)
            except TimeoutException:
                print(f"Timeout while loading: {link}")
            except NoSuchElementException:
                print(f"Element not found in: {link}")

    def save_hotels_to_csv(self, curr_time):
        print(f"Length of hotels: {len(self.hotels)}")
        print(f"Length of standard: {len(self.standard)}")
        print(f"Length of country: {len(self.country)}")
        print(f"Length of cityArrival: {len(self.cityArrival)}")
        df = pd.DataFrame({
            'hotelName': self.hotels,
            'standard': self.standard,
            'country': self.country,
            'city': self.cityArrival
        })
        output_path = f'hotels/hotels_{current_time}.csv'
        df.to_csv(output_path, index=False)
        print("Data saved to hotels.csv")

    def save_offers_to_csv(self, curr_time):
        print(f"Length of offer_names: {len(self.offer_names)}")
        print(f"Length of dateArrival: {len(self.dateArrival)}")
        print(f"Length of dateDeparture: {len(self.dateDeparture)}")
        print(f"Length of price: {len(self.price)}")

        df = pd.DataFrame({
            'offerName': self.offer_names,
            'dateEnd': self.dateArrival,
            'dateStart': self.dateDeparture,
            'basePrice': self.price
        })
        output_path = f'offers/offers_{current_time}.csv'
        df.to_csv(output_path, index=False)
        print("Offers saved to offers.csv")

    def save_transport_to_csv(self, curr_time):
        print(f"Length of offer_names: {len(self.cityArrival)}")
        print(f"Length of dateArrival: {len(self.cityDeparture)}")
        print(f"Length of dateDeparture: {len(self.dateDeparture)}")
        print(f"Length of price: {len(self.price)}")

        df = pd.DataFrame({
            'timeArrival': self.timeArrival,
            'timeDeparture': self.timeDeparture,
            'dateArrival': self.dateArrival,
            'dateDeparture': self.dateDeparture,
            'cityArrival': self.cityArrival,
            'cityDeparture': self.cityDeparture
        })
        output_path = f'transports/transports_{current_time}.csv'
        df.to_csv(output_path, index=False)
        print("Transport saved to offers.csv")

    def close_driver(self):
        self.driver.quit()


# Example usage within the class file for testing
if __name__ == "__main__":
    csv_filename = "InputData/Articles.csv"  # The CSV file containing the links
    link_visitor = LinkVisitor(csv_filename)
    link_visitor.visit_links()
    link_visitor.close_driver()
    current_time = datetime.now()
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    #link_visitor.save_offers_to_csv(current_time)
    #link_visitor.save_hotels_to_csv(current_time)
    link_visitor.save_transport_to_csv(current_time)

    url = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=%22source%3AA+%26+A+Practice%22+" \
          "OR+%22source%3AAACN+Advanced+Critical+Care%22+OR+%22source%3AAAPS+Journal%22+OR+%22source%3AAAPS+PHARMSCITECH%22+OR+%22source%3AABCD-Arquivos+Brasileiros+de+Cirurgia+Digestiva-Brazilian+Archives+of+Digestive+Surgery%22+OR+%22source%3AAbdominal+Radiology%22+OR+%22source%3AACADEMIC+EMERGENCY+MEDICINE%22+OR+%22source%3AACADEMIC+MEDICINE%22+OR+%22source%3AAcademic+Pathology%22+OR+%22source%3AAcademic+Pediatrics%22+OR+%22source%3AACADEMIC+PSYCHIATRY%22+OR+&btnG="
    soup = LinkVisitor.get_soup_from_url(url)
    links = LinkVisitor.extract_links_from_divs(soup)
    driver = linkVisitor.configure_driver()
    LinkVisitor.click_button_for_links(links, driver)
