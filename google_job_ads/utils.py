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
