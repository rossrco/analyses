import re
import os
import pandas as pd
import numpy as np
from sklearn import model_selection
from sklearn import metrics


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
    except Exception:
        return None


def get_queries(query_dir):
    queries = {}
    for query_file in (os.listdir(query_dir)):
        with open(os.path.join(query_dir, query_file), 'r') as query:
            queries[query_file] = query.read()
    return queries


def get_learning_curves(estimator, X, y, train_sizes=np.arange(0.1, 1.1, 0.1),
                        score='neg_mean_absolute_error', cv=5):
    train_sizes, train_scores, test_scores =\
        model_selection.learning_curve(estimator, X, y,
                                       train_sizes=train_sizes,
                                       scoring=score, cv=cv)
    curve_data = pd.DataFrame(columns=range(train_scores.shape[1]))
    for result, result_type in zip([train_scores, test_scores],
                                   ['train', 'test']):
        frame = pd.DataFrame(result)
        frame['size'] = train_sizes
        frame['type'] = result_type
        curve_data = curve_data.append(frame, ignore_index=True)
    curve_data = curve_data.melt(id_vars=['size', 'type'], var_name='cv_fit',
                                 value_name='score')
    return curve_data


def get_cv_res(estimator, X, y, score=['neg_mean_absolute_error'], cv=5):
    cross_val = model_selection.cross_validate(estimator, X, y, scoring=score,
                                               cv=cv)
    return cross_val


def print_cv_res(cross_val):
    for key, val in cross_val.items():
        print('Mean {}, {:.2f}'.format(key, val.mean()))


def print_scores(y_true, y_pred):
    _metrics = {'mean_absolute_error': metrics.mean_absolute_error,
                'explained_variance': metrics.explained_variance_score,
                'r2': metrics.r2_score,
                'max_error': metrics.max_error}
    for metric_name, metric in _metrics.items():
        print(metric_name + ': ' + '{:.2f}'.format(metric(y_true, y_pred)))
