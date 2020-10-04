import seaborn as sns
import matplotlib.pyplot as plt
import pickle
import numpy as np
import pandas as pd
import random
from collections import Counter


with open('n40_games100_random', 'rb')  as f:
    random_data = pickle.load(f) 
with open('n40_games100_highest_yield', 'rb')  as f:
    highest_yield_data = pickle.load(f) 

############## 5 number summary for data ############
print('Random')
print(pd.Series(data=random_data).describe(), '\n')
print('Highest Yield')
print(pd.Series(data=highest_yield_data).describe())

######## Plot data Histograms ########

f, axs = plt.subplots(2, 1, sharex=True, sharey=True)
# [0.34, 0.44, 0.45, 0.41, 0.48, 0.48, 0.33, 0.39, 0.41, 0.41, 0.33, 0.48, 0.37, 0.45, 0.36, 0.32, 0.44, 0.39, 0.44, 0.43, 0.34, 0.33, 0.4, 0.37, 0.44, 0.52, 0.4, 0.4, 0.45, 0.36, 0.38, 0.33, 0.43, 0.38, 0.42, 0.38, 0.43, 0.4, 0.43, 0.4]

random_series = pd.Series(data=random_data)
highest_yield_series = pd.Series(data=highest_yield_data)

axs[0].axvline(random_series.mean(), color='red', linestyle='--')
axs[1].axvline(highest_yield_series.mean(), color='red', linestyle='--')

random_series.plot(kind='hist', bins=10, title='Random', ax=axs[0])
highest_yield_series.plot(kind='hist', bins=10, title='Highest Yield', ax=axs[1])

f.suptitle(r'Distribution of % of games won by Random and Highest Yield Othello Bots')
plt.xlabel(r'% of games won (out of 100 games)')
plt.show()