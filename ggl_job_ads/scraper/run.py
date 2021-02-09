import io
import yaml
import time
import random
import argparse
import pandas as pd
from urllib.parse import quote
from bs4 import BeautifulSoup
from selenium import webdriver
from google.cloud import storage


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
    soup = BeautifulSoup(html, 'html.parser')
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

        ads = soup.find_all('a', config['ad_tiles'])
        i += 1
        r_button_tag = soup.find('a', config['r_button'])
        r_button = r_button_tag is not None
        for a in ads:
            yield a


def get_qual(soup, qual_type='minimum'):
    qual = []

    try:
        qualifications = soup.find('div', config['qual'])
        if qual_type == 'minimum':
            qual = qualifications.find_all('ul')[0]
        elif qual_type == 'preferred':
            qual = qualifications.find_all('ul')[1]

        qual = [el.text.strip() for el in qual.find_all('li')]
    except AttributeError:
        pass

    return '\n'.join(qual)


def get_job_descr(soup):
    job_descr = None
    try:
        job_descr = soup.find('div', config['job_descr']).text
    except AttributeError:
        pass

    return job_descr


def get_responsb(soup):
    resp = []

    try:
        resp = soup.find('div', config['responsb']).find_all('li')
        resp = [el.text.strip() for el in resp]
    except AttributeError:
        pass

    return '\n'.join(resp)


def get_job_title(soup):
    return soup.attrs.get('aria-label')


def get_ad_id(soup):
    return soup.attrs.get('data-gtm-label')


def get_job_location(soup):
    try:
        return soup.find('div', config['job_loc']).text.strip()
    except AttributeError:
        return None


def get_data(tiles):
    i = 0
    res_ads = pd.DataFrame()

    for t in tiles:
        print(f'Vieweing ad {i}', end='\r')

        ad = dict()
        ad['title'] = get_job_title(t)
        ad['id'] = get_ad_id(t)
        ad['location'] = get_job_location(t)

        ad_url = config['base_url'] + ad['id']
        ad_soup = get_page_data(ad_url)

        ad['minimum_qual'] = get_qual(ad_soup, qual_type='minimum')
        ad['preferred_qual'] = get_qual(ad_soup, qual_type='preferred')
        ad['job_descr'] = get_job_descr(ad_soup)
        ad['responsibilities'] = get_responsb(ad_soup)

        res_ads = res_ads.append(ad, ignore_index=True)
        i += 1

    return res_ads


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the crawler')

    parser.add_argument('--search_str',
                        help='Job ad search string',
                        type=str,
                        default='machine learning engineer')

    parser.add_argument('--min_wait',
                        help='Min number of seconds to wait between pages',
                        type=int,
                        default=1)

    parser.add_argument('--max_wait',
                        help='Max number of seconds to wait between pages',
                        type=int,
                        default=2)

    parser.add_argument('--max_pages',
                        help='Max number of pages to view',
                        type=int,
                        default=2)

    args = parser.parse_args()

    client = storage.Client(config['project'])
    bucket = client.get_bucket(config['bucket'])
    blob = bucket.blob(config['dest_file'])
    file_content = io.BytesIO(blob.download_as_string())

    ads = pd.read_csv(file_content)

    tiles = extract_tiles(args.search_str, args.min_wait, args.max_wait,
                          args.max_pages)
    res_ads = get_data(tiles)
    ads = ads.append(res_ads, ignore_index=True).drop_duplicates()

    blob.upload_from_string(ads.to_csv(index=False))
