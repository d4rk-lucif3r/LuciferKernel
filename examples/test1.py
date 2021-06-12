#%%
import imp
import os
os.getcwd()
#%%
os.chdir('../')
import pandas as pd

#%%
from lucifer_ml.supervised import classification as cls

# %%
dataset = pd.read_csv('examples/Social_Network_Ads.csv')
X = dataset.iloc[:, :-1]
y = dataset.iloc[:, -1]

# %%
cls1 = cls.Classification(predictor='ann', epochs=10)
# cls1.predictor()
# %%
cls1.predict(X, y)

#%%
x = X.reshape(1,-1)
# %%
x[()]
# %%
x.ndim
# %%
