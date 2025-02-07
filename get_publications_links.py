import csv
import logging
import bs4
import os
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

def configure_driver( chrome_driver_path = "./chromedriver.exe"):
    service = Service(executable_path=chrome_driver_path)
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')  # For headless browsing
    options.add_argument('--log-level=3')  # Suppress logging
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    download_dir = os.path.abspath("Downloads")  # Change this to your desired path

    prefs = {
        "download.default_directory": download_dir,  # Set the download directory
        "plugins.always_open_pdf_externally": True,  # Ensure PDFs are downloaded, not opened
        "download.prompt_for_download": False,  # Disable download prompt
        "download.directory_upgrade": True  # Allow directory upgrades
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=service, options=options)
    print("Driver initialised correctly!")
    return driver

def get_pages(driver):
    elements = driver.find_elements(By.XPATH, '//a[contains(@class, "gs_nma") and @href]')
    print(f'{len(elements)} loaded')

    return elements

def scrap(driver):
    #url = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=%22source%3AA+%26+A+Practice%22+OR+%22source%3AAACN+Advanced+Critical+Care%22+OR+%22source%3AAAPS+Journal%22+OR+%22source%3AAAPS+PHARMSCITECH%22+OR+%22source%3AABCD-Arquivos+Brasileiros+de+Cirurgia+Digestiva-Brazilian+Archives+of+Digestive+Surgery%22+OR+%22source%3AAbdominal+Radiology%22+OR+%22source%3AACADEMIC+EMERGENCY+MEDICINE%22+OR+%22source%3AACADEMIC+MEDICINE%22+OR+%22source%3AAcademic+Pathology%22+OR+%22source%3AAcademic+Pediatrics%22+OR+%22source%3AACADEMIC+PSYCHIATRY%22+&btnG="


    # elements = driver.find_elements(By.XPATH, "//a")
    elements = driver.find_elements(By.XPATH, '//a[contains(@href, ".pdf")]')
    print(elements, sep="\n")

    # Re-locate before clicking
    # pdf_link = driver.find_element(By.XPATH, '//a[contains(@href, ".pdf")]')
    # pdf_link.click()

    count = 0
    # Iterate through each element and click
    for element in elements[0:8]:
        try:

            # href = element.get_attribute('href')  # Optional: Get the link URL
            # print(f"Clicking on link: {href}")

            element.click()  # Click the link
            count += 1

            # Navigate back to the original page
            # driver.back()

        except TimeoutException:
            print(f"Timeout: Could not click link at index {element}. Proceeding to next.")
            #driver.back()

        except Exception as e:
            print("Error clicking element:", e)
            driver.back()

    print(f'Downloaded {count / len(elements)} of available reports')
    #driver.quit()

def clean_folder(folder_path):
    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        os.remove(file_path)
    print(f'Folder {folder_path} cleaned')


if __name__ == '__main__':


    driver = configure_driver()
    driver.implicitly_wait(2)
    cur_page = 1
    url = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=%22source%3AA+%26+A+Practice%22+OR+%22source%3AAACN+Advanced+Critical+Care%22+OR+%22source%3AAAPS+Journal%22+OR+%22source%3AAAPS+PHARMSCITECH%22+OR+%22source%3AABCD-Arquivos+Brasileiros+de+Cirurgia+Digestiva-Brazilian+Archives+of+Digestive+Surgery%22+OR+%22source%3AAbdominal+Radiology%22+OR+%22source%3AACADEMIC+EMERGENCY+MEDICINE%22+OR+%22source%3AACADEMIC+MEDICINE%22+OR+%22source%3AAcademic+Pathology%22+OR+%22source%3AAcademic+Pediatrics%22+OR+%22source%3AACADEMIC+PSYCHIATRY%22+&btnG="
    driver.get(url)
    driver.maximize_window()
    loaded_pages = get_pages(driver)
    loaded_pages_filtered = loaded_pages[1:9]

    #Scrap pdfs
    scrap(driver)
    driver.get(url)
    loaded_pages = get_pages(driver)
    loaded_pages_filtered = loaded_pages[1:9]
    for current_page in range(len(loaded_pages_filtered)):
        loaded_pages = get_pages(driver)
        loaded_pages_filtered = loaded_pages[1:9]
        print(len(loaded_pages_filtered))
        next_page_url = loaded_pages_filtered[current_page].get_attribute('href')
        print(next_page_url)
        try:
            driver.get(next_page_url)
            driver.maximize_window()
            scrap(driver)
            print('Page changed')
        except Exception as e:
            print("Couldnt move to the next page", e)
    driver.quit()

def scrap_many(driver, pages_to_scrape=3):
    driver.implicitly_wait(2)
    driver.maximize_window()

    for page_index in range(pages_to_scrape):
        try:
            # Load and filter next pages
            loaded_pages = get_pages(driver)
            next_page_url = loaded_pages[1:pages_to_scrape][page_index].get_attribute('href')
            print(f"Navigating to: {next_page_url}")

            # Navigate to the next page and scrape
            driver.get(next_page_url)
            scrap(driver)
            print(f"Page {page_index + 1} scraped successfully.")
        except Exception as e:
            print(f"Could not move to page {page_index + 1}: {e}")


scrap_many(driver)
