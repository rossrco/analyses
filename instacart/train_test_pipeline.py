import pandas as pd
import numpy as np
from sklearn.model_selection import learning_curve, GridSearchCV
import matplotlib.pyplot as plt
import seaborn as sns

class MultiEstimator:
    def __init__(self, estimators, scorer, train_sizes = None, cv = None):
        self.estimators = estimators
        self.scorer = scorer
        self.train_sizes = np.linspace(0.1, 1.0, 5) if not train_sizes else train_sizes
        self.cv = cv
        self.scores = {}
        self.best_estimator = None
        self.scores_frame = None

    def fit(self, X, y):
        for estimator_name in self.estimators.keys():
            train_sizes, train_scores, test_scores = learning_curve(self.estimators[estimator_name],
                                                                    X, y,
                                                                    scoring = self.scorer,
                                                                    cv = self.cv,
                                                                    train_sizes = self.train_sizes)
            self.scores[estimator_name] = dict([('train', dict(zip(train_sizes, train_scores))),
                                                ('test', dict(zip(train_sizes, test_scores)))])

            self.estimators[estimator_name].fit(X, y)

        self.train_sizes_res = train_sizes
        self.get_score_dataframe()
        self.get_best_model()

        return self

    def score(self, X, y_true):
        if self.best_estimator is None:
            raise Exception('An estimator must be selected first!')
        else:
            self.best_estimator.score(X, y_true)

        return self

    def predict(self, X):
        if self.best_estimator is None:
            raise Exception('An estimator must be selected first!')
        else:
            return self.best_estimator.predict(X)

    def predict_log_proba(self, X):
        if self.best_estimator is None:
            raise Exception('An estimator must be selected first!')
        else:
            return self.best_estimator.predict_log_proba(X)

    def predict_proba(self, X):
        if self.best_estimator is None:
            raise Exception('An estimator must be selected first!')
        else:
            return self.best_estimator.predict_proba(X)

    def draw_learning_curves(self):
        if self.scores_frame is None:
            raise Exception('Derive the scores frame first!')
        else:
            all_estimators = self.scores_frame['estimator'].unique()
            n_vertical = int(len(all_estimators) / 2) + len(all_estimators) % 2
            n_horizontal = 2
            fig = plt.figure(figsize = (n_horizontal * 5, n_vertical * 3))
            fig.suptitle('Learning Curves')
            for i, estimator in enumerate(all_estimators):
                ax = plt.subplot(n_vertical, n_horizontal, i + 1)
                ax.set_title(estimator)
                to_plot = self.scores_frame[self.scores_frame['estimator'] == estimator]
                sns.lineplot(x = 'size', y = 'score', hue = 'type', data = to_plot)
            plt.subplots_adjust(hspace = 0.5, wspace = 0.3)

    def get_scoring_report(self):
        report = pd.pivot_table(data = self.scores_frame,
                                index = 'size',
                                columns = ['estimator', 'type'],
                                values = 'score',
                                aggfunc = 'mean')

        return report

    def perform_grid_search(self, parameter_grid, X, y):
        if self.best_estimator is None:
            raise Exception('An estimator must be selected first!')
        else:
            self.grid_search_cv = GridSearchCV(estimator = self.best_estimator,
                                               param_grid = parameter_grid,
                                               scoring = self.scorer,
                                               verbose = 0)
            self.grid_search_cv.fit(X, y)
            self.best_estimator = self.grid_search_cv.best_estimator_

        return self

    def get_best_model(self):
        estimator_scores = self.scores_frame[self.scores_frame['size'] ==\
                                             self.scores_frame['size'].max()]\
        [['estimator', 'score']].groupby(by = 'estimator').mean()

        estimator_name = estimator_scores[estimator_scores['score'] ==\
                                          estimator_scores['score'].max()].index[0]

        self.best_estimator = self.estimators[estimator_name]

        return self

    def set_best_model(self, estimator_name):
        self.best_estimator = self.estimators[estimator_name]

        return self

    def get_score_dataframe(self):
        self.scores_frame = pd.DataFrame(columns = ['estimator', 'type', 'size', 'cv_fit', 'score'])
        for estimator in self.scores.keys():
            for score_type in self.scores[estimator].keys():
                for size in self.scores[estimator][score_type].keys():
                    for cv_fit, score in enumerate(self.scores[estimator][score_type][size].tolist()):
                        to_append = pd.DataFrame([[estimator, score_type, size, cv_fit, score]],
                                                 columns = self.scores_frame.columns)
                        self.scores_frame = self.scores_frame.append(to_append, ignore_index = True)

        return self
