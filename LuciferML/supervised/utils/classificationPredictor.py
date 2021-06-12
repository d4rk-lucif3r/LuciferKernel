import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import tensorflow as tf


def build_ann_model(
    input_units, hidden_layers,
    input_activation, output_activation,
    output_units, optimizer, loss, metrics
):
    try:
        classifier = tf.keras.models.Sequential()
        for i in range(0, hidden_layers):
            classifier.add(tf.keras.layers.Dense(
                units=input_units, activation=input_activation))
        classifier.add(tf.keras.layers.Dense(
            units=output_units, activation=output_activation))
        classifier.compile(optimizer=optimizer,
                        loss=loss, metrics=metrics,)
        return classifier
    except Exception as error:
        print('ANN Build Failed with error :',error, '\n')


def classificationPredictor(
        predictor, params, X_train, X_val, y_train, y_val, epochs, hidden_layers,
        input_activation, output_activation, loss,
        batch_size, metrics, validation_split, optimizer, output_units, input_units
):
    """
    Takes Predictor string , parameters , Training and Validation set and Returns a classifier for the Choosen Predictor.
    """
    try:
        if predictor == 'lr':
            print('Training Logistic Regression on Training Set [*]\n')

            classifier = LogisticRegression(**params)
            parameters = [{
                'penalty': ['l1', 'l2', 'elasticnet', 'none'],
                'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
                'C': np.logspace(-4, 4, 20),
            }]

        elif predictor == 'svm':
            print('Training Support Vector Machine on Training Set [*]\n')

            classifier = SVC(**params)
            parameters = [
                {'kernel': ['rbf'], 'gamma': [1e-3, 1e-4, 0.1, 0.2, 0.3, 0.4,
                                            0.5, 0.6, 0.7, 0.8, 0.9], 'C': np.logspace(-4, 4, 20)},
                {'kernel': ['linear'], 'gamma': [1e-3, 1e-4, 0.1, 0.2, 0.3,
                                                0.4, 0.5, 0.6, 0.7, 0.8, 0.9], 'C': np.logspace(-4, 4, 20)},
                {'kernel': ['poly'], 'gamma': [1e-3, 1e-4, 0.1, 0.2, 0.3,
                                            0.4, 0.5, 0.6, 0.7, 0.8, 0.9], 'C': np.logspace(-4, 4, 20)},
                {'kernel': ['sigmoid'], 'gamma': [1e-3, 1e-4, 0.1, 0.2, 0.3,
                                                0.4, 0.5, 0.6, 0.7, 0.8, 0.9], 'C': np.logspace(-4, 4, 20)},
            ]
        elif predictor == 'knn':
            print('Training K-Nearest Neighbours on Training Set [*]\n')

            classifier = KNeighborsClassifier(**params)
            parameters = [{
                'n_neighbors': list(range(0, 31)),
                'weights': ['uniform', 'distance'],
                'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
                'n_jobs': [1, 0, None]
            }]

        elif predictor == 'dt':
            print('Training Decision Tree Classifier on Training Set [*]\n')

            classifier = DecisionTreeClassifier(**params)
            parameters = [{
                'criterion': ['gini', 'entropy'],
                'splitter': ['best', 'random'],
                'max_features': [2, 3],
                'max_depth': [4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20, 30, 40, 50, 70, 90, 120, 150],

            }]
        elif predictor == 'nb':
            print('Training Naive Bayes Classifier on Training Set [*]\n')

            classifier = GaussianNB(**params)
            parameters = {}

        elif predictor == 'rfc':
            print('Training Random Forest Classifier on Training Set [*]\n')

            classifier = RandomForestClassifier(**params)
            parameters = [{
                'criterion': ['gini', 'entropy'],
                'n_estimators': [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 900, 1000],
                'bootstrap': [True, False],
                'max_depth': [4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20, 30, 40, 50, 70, 90, 120, 150],
                'max_features': [2, 3],
                'min_samples_leaf': [3, 4, 5],
                'min_samples_split': [8, 10, 12],
            }]
        elif predictor == 'xgb':
            print('Training XGBClassifier on Training Set [*]\n')

            classifier = XGBClassifier(**params)
            parameters = {
                'min_child_weight': [1, 5, 10],
                'gamma': [1e-3, 1e-4, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                'subsample': [0.6, 0.8, 1.0],
                'colsample_bytree': [0.6, 0.8, 1.0],
                'max_depth': [4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20, 30, 40, 50, 70, 90, 120, 150],
                'learning_rate': [0.3, 0.1, 0.03],
            }
        elif predictor == 'ann':
            print('Training ANN on Training Set [*]\n')
            classifier = build_ann_model(input_units, hidden_layers,
                                        input_activation, output_activation,
                                        output_units, optimizer, loss, metrics)
            ann_history = classifier.fit(
                X_train, y_train, validation_split=validation_split,
                validation_data=(
                    X_val, y_val), epochs=epochs, batch_size=batch_size
            )

            parameters = {'batch_size': [100, 20, 50, 25, 32],
                        'nb_epoch': [200, 100, 300, 400],
                        'input_units': [5, 6, 10, 11, 12, 15],

                        }
        return (parameters, classifier)
    except Exception as error:
        print('Model Build Failed with error :', error, '\n')
