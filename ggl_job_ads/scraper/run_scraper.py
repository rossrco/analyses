from utils import get_data, extract_tiles

if __name__ == '__main__':
    tiles = extract_tiles('machine learning engineer', 1, 2, 2)
    res_ads = get_data(tiles)
    res_ads.to_csv('job_ads.csv', mode='a', header=False)
