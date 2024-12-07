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
          return pl.DataFrame([])

def ua_picker():
    ua = UserAgent()
    user_agent = ua.random
    print(user_agent)
    return(user_agent)

def find_new_news(current_news, previous_news):
    if not previous_news.is_empty():
        return current_news.join(
            previous_news,
            on=["company", "news", "link", "date"],
            how="anti"
        )
    return current_news


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

    try:
        driver.get(url)

        input_field = wait.until(EC.visibility_of_element_located((By.ID, 'edit-titolo')))
        input_field.send_keys('prysmian')


        search_button = wait.until(EC.element_to_be_clickable((By.ID, 'edit-submit-search-news')))
        search_button.click()

        print('waiting')
        time.sleep(5)
        elements = driver.find_elements(By.CLASS_NAME, "views-row")
        data = []

        for element in elements:
            company = element.find_element(By.CLASS_NAME, 'news-azienda').text
            title = element.find_element(By.CLASS_NAME, 'news-title').text  
            link = element.find_element(By.CLASS_NAME, 'news-title').find_element(By.TAG_NAME, 'a').get_attribute('href')  
            date = element.find_element(By.CLASS_NAME, 'news-data').text  
            data.append([company, title, link, date])

        data = pl.DataFrame(data, schema=["company", "news", 'link', "date"], orient="row")

        data = data.with_columns(    pl.col("date").str.strptime(pl.Datetime, "%d/%m/%Y - %H:%M"))   
        return data
    finally:
        driver.quit()

def collect(url, previous_news):
    current_news = init_driver(url)

    new_news = find_new_news(current_news, previous_news)

    return new_news.sort('date') if not new_news.is_empty() else pl.DataFrame(
            [],
            schema={"company": pl.Utf8, "news": pl.Utf8, "link": pl.Utf8, "date": pl.Datetime}
        )

def news():
    urls = ["https://www.emarketstorage.it/it/comunicati-finanziari", "https://www.emarketstorage.it/it/documenti"]
    all_new_news = pl.DataFrame([])
    news_manager = storage_manager('news.parquet')

    previous_news = news_manager.load_data()
    print(previous_news.head(5))

    for url in urls:
        print(f"Processing URL: {url}")
        new_news = collect(url, previous_news)
        print(new_news)
        if not new_news.is_empty():
            all_new_news = pl.concat([all_new_news, new_news])
    #print(f'all new news : {all_new_news}')
    if not all_new_news.is_empty():
        updated_storage = pl.concat([previous_news, all_new_news]).unique(subset=['company', 'news',
                                                                                  'link',
                                                                                  'date']).sort('date',
                                                                                               descending=True)
        print(f'updated is: {updated_storage}')
        news_manager.save_data(updated_storage)
        print(all_new_news)
        return(all_new_news)
    else:
        print("No new news to save.")
        return pl.DataFrame([],
            schema={"company": pl.Utf8, "news": pl.Utf8, "link": pl.Utf8, "date": pl.Datetime}
        )


if __name__=="__main__":
    news()
