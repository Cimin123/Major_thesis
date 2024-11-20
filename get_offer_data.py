import csv
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from datetime import datetime

logging.getLogger('selenium').setLevel(logging.CRITICAL)

class LinkVisitor:
    def __init__(self, csv_filename):
        self.file_num = 60
        self.list_start = 32
        self.list_end = 40
        self.csv_filename = csv_filename
        self.driver = self.configure_driver()
        self.links = self.read_links_from_csv()
        self.hotels = []
        self.country = []
        self.breadcrumbs = []
        self.offer_names = []
        self.standard = []
        self.cityDeparture = []
        self.cityArrival = []
        self.timeDeparture = []
        self.timeArrival = []
        self.dateDeparture = []
        self.dateArrival = []
        self.price = []

    def configure_driver(self):
        chrome_driver_path = "./chromedriver.exe"  # Update with your correct path

        service = Service(executable_path=chrome_driver_path)
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')  # For headless browsing
        options.add_argument('--log-level=3')  # Suppress logging
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(service=service, options=options)
        return driver

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

    def extract_breadcrumb_links(self):
        try:
            breadcrumbs = self.driver.find_elements(By.CLASS_NAME, "kh-breadcrumbs__link")
            breadcrumb_links = [breadcrumb.text for breadcrumb in breadcrumbs]
            return breadcrumb_links
        except NoSuchElementException:
            return []

    def extract_data_rating(self):
        try:
            element_with_rating = self.driver.find_element(By.CSS_SELECTOR, "[data-rating]")
            rating_value = element_with_rating.get_attribute("data-rating")
            return rating_value
        except NoSuchElementException:
            return None

    def extract_span_from_paragraph(self):
        try:
            subelements = self.driver.find_elements(By.CSS_SELECTOR, "li.kh-breadcrumbs__subelement span")
            subelement_texts = [subelement.text for subelement in subelements]
            print(subelement_texts)
            return subelement_texts
        except NoSuchElementException:
            return []

    def visit_links(self):
        self.links = self.links[self.list_start:self.list_end]
        for link in self.links:
            print(f"Visiting: {link}")
            self.driver.get(link)
            try:
                # Click the button if it exists
                self.click_button_if_present("button.r-button.r-button--accent.r-button--hover.r-button--contained.r-button--only-text.r-button--svg-margin-left.r-consent-buttons__button.cmpboxbtnyes")
                self.click_button_if_present("button.r-button.r-button--uppercase.r-button--accent.r-button--hover.r-button--contained.r-button--only-text.r-button--svg-margin-left")

                #Hotele
                # header_text = self.extract_header_text()
                # if header_text:
                #     print(f"Header text: {header_text}")
                #     self.hotels.append(header_text)
                # else:
                #     print("Header element not found.")
                #     self.hotels.append(None)


                #Nazwa wycieczki
                # offer_name = self.extract_span_from_paragraph()
                # if offer_name:
                #     self.offer_names.append(offer_name)
                # else:
                #     self.offer_names.append(None)

                #Kraj/ Nazwa wycieczki
                # breadcrumb = self.extract_breadcrumb_links()
                # print(f"Breadcrumbs: {breadcrumb}")
                # self.breadcrumbs.append(breadcrumb)
                # if breadcrumb:
                #     self.country.append(breadcrumb[2])
                # else:
                #     self.country.append(None)
                # #Cena
                # offer_price = self.read_price()
                # if offer_price:
                #     self.price.append(offer_price)
                # else:
                #     self.price.append(None)

                #Gwiazdki
                # data_rating = self.extract_data_rating()
                # if data_rating:
                #     print(f"Data Rating: {data_rating}")
                #     self.standard.append(data_rating)
                # else:
                #     print("Data Rating not found.")
                #     self.standard.append(None)


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

    # def visit_links(self):
    #     for link in self.links:
    #         print(f"Visiting: {link}")
    #         self.driver.get(link)
    #         try:
    #             # Click the button if it exists
    #             self.click_button_if_present()
    #
    #             # Example: Wait for the div with class 'kh-drawer-rozklad-lotow-details__info' to be present
    #             # WebDriverWait(self.driver, 10).until(
    #             #     EC.presence_of_element_located((By.CLASS_NAME, "kh-drawer-rozklad-lotow-details__info"))
    #             # )
    #             # print(f"Successfully loaded: {link}")
    #             #
    #             # # Extract required data
    #             # self.extract_data()
    #
    #         except TimeoutException:
    #             print(f"Timeout while loading: {link}")

    def extract_flights_departure_data(self):
        try:
            info_div = self.driver.find_element(By.CLASS_NAME, "kh-drawer-rozklad-lotow-details__info")
            departure_hour = info_div.find_element(By.CLASS_NAME, "kh-drawer-rozklad-lotow-details__info-hours").text
            departure_place = info_div.find_element(By.CLASS_NAME, "kh-drawer-rozklad-lotow-details__info-airport").text
            departure_day = info_div.find_element(By.CLASS_NAME,"kh-drawer-rozklad-lotow-details__info-date").text

            self.dateDeparture.append(departure_day)
            self.timeDeparture.append(departure_hour)
            self.cityDeparture.append(departure_place)
            # info_lower_div = self.driver.find_element(By.CLASS_NAME, "kh-drawer-rozklad-lotow-details__info-top")
            # arrival_place = info_lower_div.find_element(By.CLASS_NAME,"kh-drawer-rozklad-lotow-details__info-airport").text

            print(f"Departure Hour: {departure_hour}, Departure Day:{departure_day} Departure Place: {departure_place}")

            # Optionally, you can store the extracted data in a list or write it to a CSV file

        except Exception as e:
            print(f"Error extracting data: {e}")

    def read_price(self):
        try:
            base_price = self.driver.find_element(By.CLASS_NAME, "kh-konfigurator-cena__za-osobe").text
            print(f"Base price {base_price}")
            return base_price
        except Exception as e:
            print(f"Error extracting data: {e}")

    def extract_flights_arrival_data(self):
        try:
            info_div = self.driver.find_element(By.CLASS_NAME, "kh-drawer-rozklad-lotow__return")
            arrival_hour = info_div.find_element(By.CLASS_NAME, "kh-drawer-rozklad-lotow-details__info-hours").text
            arrival_date = info_div.find_element(By.CLASS_NAME, "kh-drawer-rozklad-lotow-details__info-date").text
            arrival_place = info_div.find_element(By.CLASS_NAME, "kh-drawer-rozklad-lotow-details__info-airport").text

            print(f"Arrival Hour: {arrival_hour}, Arrival Day:{arrival_date}, Arrival Place: {arrival_place}")
            self.dateArrival.append(arrival_date)
            self.timeArrival.append(arrival_hour)
            self.cityArrival.append(arrival_place)
            # Optionally, you can store the extracted data in a list or write it to a CSV file

        except Exception as e:
            print(f"Error extracting data: {e}")

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
    csv_filename = "links.csv"  # The CSV file containing the links
    link_visitor = LinkVisitor(csv_filename)
    link_visitor.visit_links()
    link_visitor.close_driver()
    current_time = datetime.now()
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    #link_visitor.save_offers_to_csv(current_time)
    #link_visitor.save_hotels_to_csv(current_time)
    link_visitor.save_transport_to_csv(current_time)
