import re
import os
import pandas as pd


def get_data(queries, query_file, client):
    request = queries[query_file]
    data = client.query(request).to_dataframe()
    return data


def get_energy_cols(data):
    energy_cols = ['energy_letter', 'energy_color']

    energy_res = [[c.strip() for c in char.split('-')]
                  if char is not None and '-' in char
                  else [None, None]
                  for char in data.energy_character]

    return pd.DataFrame(energy_res, columns=energy_cols, index=data.index)


def get_postcode_from_address(address):
    try:
        return re.search(r'(.*)(\d{4})(.*)', address, re.I)[2]
    except Exception as e:
        return None


def get_queries(query_dir):
    queries = {}
    for query_file in (os.listdir(query_dir)):
        with open(os.path.join(query_dir, query_file), 'r') as query:
            queries[query_file] = query.read()
    return queries