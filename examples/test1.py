# #%%

import os
# os.getcwd()
#%%
import pandas as pd

#%%
import lucifer_ml

# %%
dataset = pd.read_csv('examples/Social_Network_Ads.csv')
X = dataset.iloc[:, :-1]
y = dataset.iloc[:, -1]

# %%
cls1 = cls.Classification(predictor='ann', epochs=10)
# cls1.predictor()
# %%
cls1.predict(X, y)


