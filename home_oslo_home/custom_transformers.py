from sklearn import base
from google.cloud import bigquery
import utils as u

queries = u.get_queries('queries')
bq_client = bigquery.Client()


class PostCodeExtractor(base.TransformerMixin, base.BaseEstimator):
    '''Extract the post code from the address column
    and drop the address column'''

    def __inint__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_c = X.copy()
        X_c['post_code'] = X_c['address'].str.extract(r'.*(\d{4}).*',
                                                      expand=False)
        return X_c


class PostCodeEnricher(base.TransformerMixin, base.BaseEstimator):
    '''Extract the post code data from bigquery,
    merge it with the training data.'''

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        post_codes = u.get_data(queries,
                                'post_code_area_name.sql',
                                bq_client).set_index('post_code', drop=True)
        X = X.merge(post_codes,
                    how='left',
                    left_on='post_code',
                    right_index=True)
        return X


class GmapsPlaceEnricher(base.TransformerMixin, base.BaseEstimator):
    '''Extract the gmaps data from bigquery,
    merge it with the training data.'''

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        gmaps = u.get_data(queries,
                           'gmaps_lodging_dining_places.sql',
                           bq_client).set_index('post_code', drop=True)
        X = X.merge(gmaps, how='left', left_on='post_code', right_index=True)
        return X


class NhsDataEnricher(base.TransformerMixin, base.BaseEstimator):
    '''Extract the nhs data from bigquery,
    merge it with the training data.'''

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        nhs = u.get_data(queries,
                         'uni_graduates_by_area_name.sql',
                         bq_client).set_index('area_name', drop=True)
        X = X.merge(nhs, how='left', left_on='area_name', right_index=True)
        return X


class HistoricDataEnricher(base.TransformerMixin, base.BaseEstimator):
    '''Extract the mean historic prices per
    post cide and merge them with the
    training data'''

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        historic = u.get_data(queries,
                              'aggregate_price_last_n_months.sql',
                              bq_client).set_index('post_code', drop=True)
        X = X.merge(historic,
                    how='left',
                    left_on='post_code',
                    right_index=True)
        return X


class AuxiliaryColumnRemover(base.TransformerMixin, base.BaseEstimator):
    '''Remove the helper columns.'''

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X.drop(['post_code', 'area_name', 'settlement_name', 'address'],
               axis=1,
               inplace=True)
        return X


class CustomImputer(base.TransformerMixin, base.BaseEstimator):
    '''Impute various columns.'''

    def __init__(self):
        pass

    def fit(self, X, y=None):
        self.columns = X.columns
        return self

    def transform(self, X):
        X['floor'].fillna(1, inplace=True)
        X['time_s'].fillna(60 * 60 * 4, inplace=True)
        X['num_bedrooms'].fillna(0, inplace=True)
        X['num_lodging_places'].fillna(0, inplace=True)
        X['num_dining_places'].fillna(0, inplace=True)
        # X['median_price_per_sq_m'].fillna(X.median_price_per_sq_m.median(),
        #                                   inplace=True)
        X['uni_graduates'].fillna(X.uni_graduates.mean(), inplace=True)
        return X
