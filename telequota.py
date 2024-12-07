import polars as pl

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from fake_useragent import UserAgent

import time

import os

class storage_manager:
    def __init__(self, storage_path):
        self.storage_path = storage_path

    def load_data(self):
        if os.path.exists(self.storage_path):
            return pl.read_parquet(self.storage_path)
        return pl.DataFrame([])

    def save_data(self, data):
        data.write_parquet(self.storage_path)

def ua_picker():
    ua = UserAgent()
    user_agent = ua.random
    print(user_agent)
    return(user_agent)

def wait_for_page_to_load(driver, timeout=30):
    ###Wait until the page is fully loaded
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def init_driver(url):
    firefox_profile = FirefoxProfile()
    firefox_profile.set_preference("general.useragent.override", ua_picker())
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    firefox_options.profile = firefox_profile
    driver = webdriver.Firefox(options = firefox_options)
    wait = WebDriverWait(driver, 90)

    #price = page.find(id='ctl00_phContents_ctlHeader_lblPrice').text
    #print(price)

    try:
       driver.get(url)
       wait_for_page_to_load(driver)

       price = driver.find_element(By.ID, 'ctl00_phContents_ctlHeader_lblPrice').text
       print(price)

       last_update = driver.find_element(By.XPATH,
                                         '/html/body/form/div[3]/div/div[2]/div[1]/div[2]/p/strong').text
       print(last_update)
       return(price)

    finally:
        driver.quit()


def prezzo():
    price = init_driver('https://www.teleborsa.it/azioni/prysmian-pry-it0004176001-SVQwMDA0MTc2MDAx')
    return(price)

if __name__=="__main__":
    prezzo()
