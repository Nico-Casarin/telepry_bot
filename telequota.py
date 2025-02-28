import time
from datetime import datetime, timedelta
import os

import polars as pl

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from fake_useragent import UserAgent


class storage_manager:
    def __init__(self, storage_path):
        self.storage_path = storage_path

    def load_data(self):
        if os.path.exists(self.storage_path):
            return pl.read_parquet(self.storage_path)
        return pl.DataFrame({
            "price": pl.Series([], dtype=pl.Float64),
            "timestamp": pl.Series([], dtype=pl.Datetime)
        })

    def save_data(self, data):
        data.write_parquet(self.storage_path)

class WebDriverManager:
    def __init__(self, headless=True, driver_path=None):
        self.headless = headless
        self.driver_path = driver_path
        self.driver = None

    def ua_picker(self):
        ua = UserAgent()
        user_agent = ua.random
        print(user_agent)
        return(user_agent)

    def wait_for_page_to_load(self, timeout=30):
        if self.driver:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

    def quit_driver(self):
        if self.driver:
            self.driver.quit()

    def init_driver(self):
        firefox_profile = FirefoxProfile()
        firefox_profile.set_preference("general.useragent.override", self.ua_picker())
        firefox_options = Options()
        if self.headless:
            firefox_options.add_argument('--headless')
        firefox_options.profile = firefox_profile

        service = Service(self.driver_path) if self.driver_path else None
        self.driver = webdriver.Firefox(service=service, options=firefox_options)
        print(f"Driver initialized: {self.driver}")
        return self.driver


def fetch_price(url, headless=True, driver_path=None):

    manager = WebDriverManager(headless=headless, driver_path=driver_path)
    driver = None
    print(driver)

    try:
        print("Initializing driver")
        driver = manager.init_driver()

        print(f"navigating to url: {url}")
        driver.get(url)
        manager.wait_for_page_to_load()

        price = driver.find_element(By.ID, 'ctl00_phContents_ctlHeader_lblPrice').text

        last_update = driver.find_element(By.XPATH,
                                          '/html/body/form/div[3]/div/div[2]/div[1]/div[2]/p/strong').text

        print(last_update)
        try:
            last_update = datetime.strptime(last_update.strip(), "%d/%m/%Y %H.%M")
        except ValueError:
            try:
                last_update = datetime.combine(
                    datetime.strptime(last_update.strip(), "%d/%m/%Y"),
                    (datetime.now() - timedelta(minutes=15)).time())
            except Exception:
                last_update = datetime.now()


        price = float(price.replace(",", "."))
        #last_update = datetime.combine(
         #   parsed_date,
            #datetime.strptime(last_update.strip(), "%d/%m/%Y %H.%M"),
          #  (datetime.now() - timedelta(minutes=15)).time()
        #)

        # Create a DataFrame with the extracted data
        new_row = pl.DataFrame({
            "price": [price],
            "timestamp": [last_update]
        })

        return new_row

    except Exception as e:
        print(driver)
        print(f"An error occurred: {e}")
        return pl.DataFrame({
            "price": pl.Series([], dtype=pl.Float64),
            "timestamp": pl.Series([], dtype=pl.Datetime)
        })

    finally:
        manager.quit_driver()

def prezzo(driver_path=None):

    data_manager = storage_manager('stock.parquet')
    stock_data = data_manager.load_data()
    print(stock_data)

    start_time = datetime.strptime("08:00", "%H:%M").time()
    end_time = datetime.strptime("16:30", "%H:%M").time()

    driver_path = driver_path if driver_path else None

    new_row = fetch_price(
        url='https://www.teleborsa.it/azioni/prysmian-pry-it0004176001-SVQwMDA0MTc2MDAx',
        driver_path = driver_path,
        headless=True
    )
    print(f"new row is {new_row}")

    filtered_row = new_row.filter(
        (new_row["timestamp"].dt.time() >= start_time) &
        (new_row["timestamp"].dt.time() <= end_time)
    )

    if filtered_row.shape[0] > 0:
        stock_data = stock_data.vstack(filtered_row)
        data_manager.save_data(stock_data)

    return new_row

def print_stock():
    data_manager = storage_manager('stock.parquet')
    stock_data = data_manager.load_data()
    return stock_data.head()

if __name__=="__main__":
    prezzo()

