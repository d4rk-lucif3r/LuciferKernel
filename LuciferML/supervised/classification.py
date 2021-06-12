import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import seaborn as sns
import tensorflow as tf
from imblearn.over_sampling import SMOTE
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA, KernelPCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import (GridSearchCV, cross_val_score,
                                     train_test_split)
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier


class Classification:

    def __init__(self,
                 predictor='lr',
                 params={},
                 tune=False,
                 test_size=.2,
                 cv_folds=10,
                 random_state=42,
                 pca_kernel='linear',
                 n_components_lda=1,
                 lda='n', pca='n',
                 n_components_pca=2,
                 hidden_layers=4,
                 output_units=1,
                 input_units=6,
                 input_activation='relu',
                 output_activation='sigmoid',
                 optimizer='adam',
                 metrics=['accuracy'],
                 loss='binary_crossentropy',
                 validation_split=.20,
                 epochs=100,
                 batch_size=32,
                 ):
        """
        Encode Categorical Data then Applies SMOTE , Splits the features and labels in training and validation sets with test_size = .2 , scales X_train, X_val using StandardScaler.
        Fits every model on training set and predicts results find and plots Confusion Matrix, 
        finds accuracy of model applies K-Fold Cross Validation 
        and stores its accuracies in a dictionary containing Model name as Key and accuracies as values and returns it
        Applies GridSearch Cross Validation and gives best self.params out from param list.

        Parameters:
            features : array 
                        features array

            lables : array
                        labels array

            prediself.ctor : str
                        Predicting model to be used
                        Default 'lr'
                            Prediself.ctor Strings:
                                lr - Logisitic Regression
                                svm -SupportVector Machine
                                knn - K-Nearest Neighbours
                                dt - Decision Trees
                                nb - GaussianNaive bayes
                                rfc- Random Forest Classifier
                                xgb- XGBoost Classifier
                                ann - Artificial Neural Network
            self.params : dict
                        contains parameters for model
            tune : boolean  
                    when True Applies GridSearch CrossValidation   
                    Default is False

            test_size: float or int, default=.2
                        If float, should be between 0.0 and 1.0 and represent 
                        the proportion of the dataset to include in 
                        the test split.
                        If int, represents the absolute number of test samples. 

            cv_folds : int
                    No. of cross validation folds. Default = 10
            pca : str
                if 'y' will apply PCA on Train and Validation set. Default = 'n'
            lda : str
                if 'y' will apply LDA on Train and Validation set. Default = 'n'
            pca_kernel : str
                    Kernel to be use in PCA. Default = 'linear'
            n_components_lda : int
                    No. of components for LDA. Default = 1
            n_components_pca : int
                    No. of components for PCA. Default = 2
            self.hidden_layers : int
                    No. of default layers of ann. Default = 4
            inputs_units : int
                    No. of units in input layer. Default = 6
            output_units : int
                    No. of units in output layer. Default = 6
            self.input_activation : str 
                    Activation function for Hidden layers. Default = 'relu'
            self.output_activation : str 
                    Activation function for Output layers. Default = 'sigmoid'
            optimizer: str
                    Optimizer for ann. Default = 'adam'
            loss : str
                    loss method for ann. Default = 'binary_crossentropy'
            validation_split : float or int
                    Percentage of validation set splitting in ann. Default = .20
            epochs : int
                    No. of epochs for ann. Default = 100
            batch_size :
                    Batch Size for ANN. Default = 32 


        Example:

            from luciferml.supervised import classification as cls
            dataset = pd.read_csv('Social_Network_Ads.csv')
            X = dataset.iloc[:, :-1]
            y = dataset.iloc[:, -1]
            cls.Classification(predictor = 'lr').predict(X, y)

        """
        


        self.predictor = predictor
        self.params = params
        self.tune = tune
        self.test_size = test_size
        self.cv_folds = cv_folds
        self.random_state = random_state
        self.pca_kernel = pca_kernel
        self.n_components_lda = n_components_lda
        self.lda = lda
        self.pca = pca
        self.n_components_pca = n_components_pca
        self.hidden_layers = hidden_layers
        self.output_units = output_units
        self.input_units = input_units
        self.input_activation = input_activation
        self.output_activation = output_activation
        self.optimizer = optimizer
        self.metrics = metrics
        self.loss = loss
        self.validation_split = validation_split
        self.epochs = epochs
        self.batch_size = batch_size
        self.accuracy_scores = {}

        

    def predict(self, features, labels):
        self.features = features
        self.labels = labels
        
        # Time Function ---------------------------------------------------------------------

        start = time.time()
        print("Started Predictor \n")

        # CHECKUP ---------------------------------------------------------------------
        if not isinstance(self.features, pd.DataFrame) and not isinstance(self.labels, pd.Series):
            print('TypeError: This Function take features as Pandas Dataframe and labels as Pandas Series. Please check your implementation.\n')
            end = time.time()
            print(end - start)
            return

        # Encoding ---------------------------------------------------------------------
        print('Checking if labels or features are categorical! [*]\n')
        cat_features = [
            i for i in self.features.columns if self.features.dtypes[i] == 'object']
        if len(cat_features) >= 1:
            index = []
            for i in range(0, len(cat_features)):
                index.append(self.features.columns.get_loc(cat_features[i]))
            print('Features are Categorical\n')

            ct = ColumnTransformer(
                transformers=[('encoder', OneHotEncoder(), index)], remainder='passthrough')
            print('Encoding Features [*]\n')
            features = np.array(ct.fit_transform(self.features))
            print('Encoding Features Done [', u'\u2713', ']\n')
        if self.labels.dtype == 'O':

            le = LabelEncoder()
            print('Labels are Categorical [*] \n')
            print('Encoding Labels \n')
            labels = le.fit_transform(self.labels)
            print('Encoding Labels Done [', u'\u2713', ']\n')
        else:
            print(
                'Features and labels are not categorical [', u'\u2713', ']\n')

        # Sparse Check -------------------------------------------------------------
        try:
            if scipy.sparse.issparse(self.features[()]):
                print('Converting Sparse Features to array []\n')
                self.features = self.features[()].toarray()
                print(
                    'Conversion of Sparse Features to array Done [', u'\u2713', ']\n')

            if scipy.sparse.issparse(self.labels[()]):
                print('Converting Sparse Labels to array []\n')
                self.labels = self.labels[()].toarray()
                print(
                    'Conversion of Sparse Labels to array Done [', u'\u2713', ']\n')
        except KeyError as error:
            # print(error)
            pass
        # SMOTE ---------------------------------------------------------------------
        print('Applying SMOTE [*]\n')

        sm = SMOTE(k_neighbors=4)
        self.features, self.labels = sm.fit_resample(self.features, self.labels)
        print('SMOTE Done [', u'\u2713', ']\n')

        # Splitting ---------------------------------------------------------------------
        print('Splitting Data into Train and Validation Sets [*]\n')

        X_train, X_val, y_train, y_val = train_test_split(
            self.features, self.labels, test_size=self.test_size, random_state=self.random_state)
        print('Splitting Done [', u'\u2713', ']\n')

        # Scaling ---------------------------------------------------------------------
        print('Scaling Training and Test Sets [*]\n')

        sc = StandardScaler()
        X_train = sc.fit_transform(X_train)
        X_val = sc.transform(X_val)
        print('Scaling Done [', u'\u2713', ']\n')

        # Dimensionality Reduction---------------------------------------------------------------------
        if self.lda == 'y':
            print('Applying LDA [*]\n')

            lda = LDA(n_components=self.n_components_lda)
            X_train = lda.fit_transform(X_train, y_train)
            X_val = lda.transform(X_val)
            print('LDA Done [', u'\u2713', ']\n')
        if self.pca == 'y' and not lda == 'y':
            print('Applying PCA [*]\n')
            if not self.pca_kernel == 'linear':
                try:

                    kpca = KernelPCA(
                        n_components=self.n_components_pca, kernel=self.pca_kernel)
                    X_train = kpca.fit_transform(X_train)
                    X_val = kpca.transform(X_val)
                except MemoryError as error:
                    print(error)
                    end = time.time()
                    print(end - start)
                    return

            elif self.pca_kernel == 'linear':

                pca = PCA(n_components=self.n_components_pca)
                X_train = pca.fit_transform(X_train)
                X_val = pca.transform(X_val)
            else:
                print('Un-identified PCA Kernel')
                return
            print('PCA Done [', u'\u2713', ']\n')

        # Models ---------------------------------------------------------------------
        if self.predictor == 'lr':
            print('Training Logistic Regression on Training Set [*]\n')

            classifier = LogisticRegression(**self.params)
            parameters = [{
                'penalty': ['l1', 'l2', 'elasticnet', 'none'],
                'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
                'C': np.logspace(-4, 4, 20),
            }]

        elif self.predictor == 'svm':
            print('Training Support Vector Machine on Training Set [*]\n')

            classifier = SVC(**self.params)
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
        elif self.predictor == 'knn':
            print('Training K-Nearest Neighbours on Training Set [*]\n')

            classifier = KNeighborsClassifier(**self.params)
            parameters = [{
                'n_neighbors': list(range(0, 31)),
                'weights': ['uniform', 'distance'],
                'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
                'n_jobs': [1, 0, None]
            }]

        elif self.predictor == 'dt':
            print('Training Decision Tree Classifier on Training Set [*]\n')

            classifier = DecisionTreeClassifier(**self.params)
            parameters = [{
                'criterion': ['gini', 'entropy'],
                'splitter': ['best', 'random'],
                'max_features': [2, 3],
                'max_depth': [4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20, 30, 40, 50, 70, 90, 120, 150],

            }]
        elif self.predictor == 'nb':
            print('Training Naive Bayes Classifier on Training Set [*]\n')

            classifier = GaussianNB(**self.params)

        elif self.predictor == 'rfc':
            print('Training Random Forest Classifier on Training Set [*]\n')

            classifier = RandomForestClassifier(**self.params)
            parameters = [{
                'criterion': ['gini', 'entropy'],
                'n_estimators': [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 900, 1000],
                'bootstrap': [True, False],
                'max_depth': [4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20, 30, 40, 50, 70, 90, 120, 150],
                'max_features': [2, 3],
                'min_samples_leaf': [3, 4, 5],
                'min_samples_split': [8, 10, 12],
            }]
        elif self.predictor == 'xgb':
            print('Training XGBClassifier on Training Set [*]\n')

            classifier = XGBClassifier(**self.params)
            parameters = {
                'min_child_weight': [1, 5, 10],
                'gamma': [1e-3, 1e-4, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                'subsample': [0.6, 0.8, 1.0],
                'colsample_bytree': [0.6, 0.8, 1.0],
                'max_depth': [4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20, 30, 40, 50, 70, 90, 120, 150],
                'learning_rate': [0.3, 0.1, 0.03],
            }
        elif self.predictor == 'ann':
            print('Training ANN on Training Set [*]\n')

            def build_ann_model(input_units):

                classifier = tf.keras.models.Sequential()
                for i in range(0, self.hidden_layers):
                    classifier.add(tf.keras.layers.Dense(
                        units=input_units, activation=self.input_activation))
                classifier.add(tf.keras.layers.Dense(
                    units=self.output_units, activation=self.output_activation))
                classifier.compile(optimizer=self.optimizer,
                                   loss=self.loss, metrics=self.metrics,)
                return classifier
            classifier = build_ann_model(self.input_units)
            ann_history = classifier.fit(
                X_train, y_train, validation_split=self.validation_split,
                validation_data=(
                    X_val, y_val), epochs=self.epochs, batch_size=self.batch_size
            )

            parameters = {'batch_size': [100, 20, 50, 25, 32],
                          'nb_epoch': [200, 100, 300, 400],
                          'input_units': [5, 6, 10, 11, 12, 15],

                          }

        if not self.predictor == 'ann':
            classifier.fit(X_train, y_train)
        print('Model Training Done [', u'\u2713', ']\n')

        # Confusion Matrix --------------------------------------------------------------
        print('''Making Confusion Matrix [*]''')

        y_pred = classifier.predict(X_val)
        if self.predictor == 'ann':
            y_pred = (y_pred > 0.5)
        cm = confusion_matrix(y_val, y_pred)
        print(cm)
        print('Confusion Matrix Done [', u'\u2713', ']\n')
        ax = plt.subplot()
        sns.heatmap(cm, annot=True, fmt='g', ax=ax)
        ax.set_xlabel('Predicted labels')
        ax.set_ylabel('True labels')
        ax.set_title('Confusion Matrix')
        ax.xaxis.set_ticklabels(['0', '1'])
        ax.yaxis.set_ticklabels(['0', '1'])

        # Accuracy ---------------------------------------------------------------------
        print('''Evaluating Model Performance [*]''')
        accuracy = accuracy_score(y_val, y_pred)
        print('Validation Accuracy is :', accuracy)
        print('Evaluating Model Performance [', u'\u2713', ']\n')

        # K-Fold ---------------------------------------------------------------------
        print('Applying K-Fold Cross validation [*]')
        if self.predictor == 'ann':
            classifier = tf.keras.wrappers.scikit_learn.KerasClassifier(
                build_fn=build_ann_model, verbose=1, input_units=self.input_units,
                epochs=self.epochs, batch_size=self.batch_size
            )
        accuracies = cross_val_score(
            estimator=classifier, X=X_train, y=y_train, cv=self.cv_folds, scoring='accuracy')
        print("Accuracy: {:.2f} %".format(accuracies.mean()*100))
        if not self.predictor == 'ann':
            self.accuracy_scores[classifier] = accuracies.mean()*100
        if self.predictor == 'ann':
            self.accuracy_scores['ANN'] = accuracies.mean()*100
        print("Standard Deviation: {:.2f} %".format(accuracies.std()*100))
        print('K-Fold Cross validation [', u'\u2713', ']\n')
        # GridSearch ---------------------------------------------------------------------
        if not self.predictor == 'nb' and self.tune:
            print('Applying Grid Search Cross validation [*]')

            grid_search = GridSearchCV(
                estimator=classifier,
                param_grid=parameters,
                scoring='accuracy',
                cv=self.cv_folds,
                n_jobs=-1,
                verbose=4,
            )
            grid_search.fit(X_train, y_train)
            best_accuracy = grid_search.best_score_
            best_parameters = grid_search.best_self.params_
            print("Best Accuracy: {:.2f} %".format(best_accuracy*100))
            print("Best Parameters:", best_parameters)
            print('Applying Grid Search Cross validation [', u'\u2713', ']\n')

        print('Complete [', u'\u2713', ']\n')
        end = time.time()
        print('Time Elapsed : ', end - start, 'seconds \n')
