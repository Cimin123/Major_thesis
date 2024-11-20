import urllib.request

import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from destinations import Destinations
from trips import Trips
from offers import Offers

class Scrapper:
    def __init__(self, url):
        self.driver = self.configure_driver()
        self.url = url
        self.driver.get(self.url)
        self.number_of_pages = 5
        self.scroll_speed = 50
        self.scroll_position_end = 6000

    def configure_driver(self):
        driver = webdriver.Chrome(executable_path="./chromedriver.exe")

        return driver

    def get_destinations(self):
        dest = Destinations()

        try:
            WebDriverWait(self.driver, 5).until(lambda s: s.find_element_by_id("hotels-switcher-box"))
        except TimeoutException:
            print("TimeoutException: Element not found")
            return None

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        for destination_page in soup.select("optgroup"):
            for destination in destination_page.select("option"):
                dest.destination = destination.text
                dest.write_to_json_file()

    def get_trips(self):

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        classes = ['type-1 active', 'type0', 'type5', 'type6', 'type7', 'type9', 'type11']

        for c in classes:
            t = soup.find('label', {'class': c}) # or span
            trips = Trips(t)
            trips.write_to_json_file()

    def get_offers(self):
        search_button = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/form[1]/div[4]/div[8]/button")
        search_button.click()

        cookie_button = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/p/button")
        if cookie_button is not None:
            cookie_button.click()

        for i in range(self.number_of_pages):
            self.scroll_down(self.scroll_speed)
            self.show_more_offers()
        self.scroll_up()

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        all_offers = soup.find_all('article', {'class': "offer clearfix"})
        all_offers_promo = soup.find_all('article', {'class': "offer promoOffer clearfix"})

        for offer in all_offers:
            departure, room, transport  = self.check_offer_details(offer)
            of = Offers(offer, departure, room, transport)
            of.write_to_json_file()

        for offer in all_offers_promo:
            departure, room, transport = self.check_offer_details(offer)
            of = Offers(offer, departure, room, transport)
            of.write_to_json_file()

    def show_more_offers(self):
        show_more = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[13]/div/div/section/div/div[1]/div[2]/div[1]")
        show_more.click()

    def scroll_down(self, speed):
        current_scroll_position, new_height = 0, 1
        while current_scroll_position <= new_height and current_scroll_position < self.scroll_position_end:
            current_scroll_position += speed
            self.driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            new_height = self.driver.execute_script("return document.body.scrollHeight")

    def scroll_up(self):
        self.driver.execute_script("window.scrollTo(0, 200)")

    def check_offer_details(self, offer: bs4.element.Tag):
        offer_url = offer.find('a', {'class': 'offer_link pull-right'}).get('href')
        new_url = self.url + offer_url

        self.driver.get(new_url)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        departure = soup.find('select', {'id': "departure-select"})

        try:
            departures = departure.find_all('option')
        except Exception as e:
            try:
                departures = departure.find('option')
            except Exception as e:
                departures = []

        result_departure = ""

        for d in range(len(departures)):
            departures[d] = departures[d].get_text()
            result_departure += departures[d].strip('\n')

            if d < len(departures) - 1:
                result_departure += "\\"

        room = soup.find('select', {'id': "room-select"})
        try:
            room = room.find('option').get_text()
            room = room.strip('\n')
        except Exception as e:
            room = ""

        try:
            transport = soup.find('div', {'class': "fRow own-departure-hidden fFly check-timetable-holder"})
            transport.find('a', {'id': 'check-timetable'}).get_text()
            transport = "Dojazd własny"
        except Exception as e:
            transport = "Samolot"

        return result_departure, room, transport







