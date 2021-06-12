from sklearn.model_selection import GridSearchCV


def hyperTune(classifier, parameters, X_train, y_train, cv_folds):
    """
    Takes classifier, tune-parameters, Training Data and no. of folds as input and Performs GridSearch Crossvalidation.
    """
    try:
        print('Applying Grid Search Cross validation [*]')

        grid_search = GridSearchCV(
            estimator=classifier,
            param_grid=parameters,
            scoring='accuracy',
            cv=cv_folds,
            n_jobs=-1,
            verbose=4,
        )
        grid_search.fit(X_train, y_train)
        best_accuracy = grid_search.best_score_
        best_parameters = grid_search.best_params_
        print("Best Accuracy: {:.2f} %".format(best_accuracy*100))
        print("Best Parameters:", best_parameters)
        print('Applying Grid Search Cross validation [', u'\u2713', ']\n')
    except Exception as error:
        print('HyperParam Tuning Failed with Error: ', error,'\n')
