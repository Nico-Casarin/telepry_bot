import polars as pl

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

import os

def load_storage_data(storage_path):
    ### Load old news
    if os.path.exists(storage_path):
        return pl.read_parquet(storage_path)
    return pl.DataFrame([]) ### Empty df is storage is not there


def save_storage_data(storage_path, data):
    ### Save updated storage with new news
    data.write_parquet(storage_path)

def find_new_news(current_news, previous_news):
    if not previous_news.is_empty():
        latest_date = previous_news['date'].max()
        return current_news.filter(pl.col('date') > latest_date)
    return current_news

def wait_for_page_to_load(driver, timeout=30):
    ###Wait until the page is fully loaded
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def init_driver(url):
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(options = firefox_options)
    wait = WebDriverWait(driver, 90)

    try: 
        driver.get(url)

        input_field = wait.until(EC.visibility_of_element_located((By.ID, 'edit-titolo')))
        input_field.send_keys('prysmian')


        search_button = wait.until(EC.element_to_be_clickable((By.ID, 'edit-submit-search-news')))
        search_button.click()

        #wait_for_page_to_load(driver)
        print('waiting')
        time.sleep(5)
        
        elements = driver.find_elements(By.CLASS_NAME, "views-row")
        #wait_for_page_to_load(driver)

        #print(type(elements))
        #print(len(elements))
        #print(elements)

        #elements = wait.until(EC.presence_of_all_elements_located(By.CLASS_NAME, 'views-row'))

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


def news():
    storage_path = 'news.parquet'
    previous_news = load_storage_data(storage_path)
    #print(previous_news.head(3))

    url = "https://www.emarketstorage.it/it/comunicati-finanziari"
    current_news = init_driver(url)

    new_news = find_new_news(current_news, previous_news)
    print(new_news)

    if not new_news.is_empty():
        rows = new_news
        rows = rows.sort('date')
        updated_data = pl.concat([previous_news,
                                  new_news]).unique(subset=['company','news','link','date'])
        updated_data = updated_data.sort('date', descending=True)
        updated_data.write_parquet(storage_path)
        return(rows)
    else:
        return("no news available!")


if __name__=="__main__":
    news()
