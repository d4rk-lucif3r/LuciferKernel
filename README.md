# LuciferML a Semi-Automated Machine Learning Library by d4rk-lucif3r

## About

The LuciferML is a Semi-Automated Machine Learning Python Library that works with tabular data. It is designed to save time while doing data analysis. It will help you right from data preprocessing to Data Prediction.

### The LuciferML will help you with:

1. Preprocessing Data:
    - Emcoding
    - Splitting
    - Scaling
    - Dimensionality Reduction
    - Resampling
2. Trying many different machine learning models with hyperparameter tuning,

## Installation
    
    pip install lucifer-ml


## Available Modelling Techniques: 

1) Classification 
    
    Available Predictors for Classification
    
        - lr - Logisitic Regression
        - svm - SupportVector Machine
        - knn - K-Nearest Neighbours
        - dt - Decision Trees
        - nb - GaussianNaive bayes
        - rfc- Random Forest Classifier
        - xgb- XGBoost Classifier
        - ann - Artificial Neural Network

    Example:
    
        from luciferml.supervised import classification as cls
        dataset = pd.read_csv('Social_Network_Ads.csv')
        X = dataset.iloc[:, :-1]
        y = dataset.iloc[:, -1]
        cls.Classification(predictor = 'lr').predict(X, y)

    More About [Classification](https://github.com/d4rk-lucif3r/LuciferML/blob/master/LuciferML/supervised/Classification_README.md)

    
## Note - As of v0.0.5 it LuciferML supports only Classification.
## More To be Added Soon
