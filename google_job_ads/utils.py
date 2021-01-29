import yaml
import time
import random
import pandas as pd
from urllib.parse import quote
from bs4 import BeautifulSoup
from selenium import webdriver


with open('config.yaml', 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.SafeLoader)


options = webdriver.ChromeOptions()
options.headless = True
options.add_argument('--enable-javascript')


def get_page_data(url, js_wait_time=2):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(js_wait_time)  # load the js
    html = driver.page_source
    soup = BeautifulSoup(html)
    return soup


def get_page_url(page_num, search_str):
    return config['base_url'] + f'?page={page_num}' + '&q=' + quote(search_str)


def extract_tiles(search_str, min_wait, max_wait, max_pages):
    i = 1
    r_button = True

    while i <= max_pages and r_button:
        time.sleep(random.randint(min_wait, max_wait))
        page_url = get_page_url(i, search_str)

        soup = get_page_data(page_url)

        ads = soup.find_all('a', {'class': 'gc-card'})
        i += 1
        r_button_tag = soup.find('a', config['r_button'])
        r_button = r_button_tag is not None
        for a in ads:
            yield a


def extract_qualifications(soup, qual_type='minimum'):
    qual = []

    try:
        qualifications = soup.find('div', {'itemprop': 'qualifications'})
        if qual_type == 'minimum':
            qual = qualifications.find_all('ul')[0]
        elif qual_type == 'preferred':
            qual = qualifications.find_all('ul')[1]

        qual = [el.text.strip() for el in qual.find_all('li')]
    except AttributeError:
        pass

    return qual
