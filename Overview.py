# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 22:24:04 2020

@author: tirso
"""
import os
import pandas as pd
import seaborn as sns; sns.set(style="ticks")
import matplotlib.pyplot as plt

sitreps = r'C:\Users\tirso\Documents\GitHub\COVID-19\csse_covid_19_data\csse_covid_19_time_series'
os.chdir(sitreps)

# load the csv to a pandas df
c_df = pd.read_csv('time_series_covid19_confirmed_global.csv')

# replace nans with empty strings
c_df['Province/State'] = c_df['Province/State'].fillna('')

# set place as index
# first combine the two initial columns into one
c_df['Place'] = c_df['Country/Region'] + '//' + c_df['Province/State']
# now set the new column as index
c_df.set_index('Place', inplace=True)

# drop columns we won't need
c_df.drop(['Province/State','Country/Region','Lat','Long'],axis=1,inplace=True)

# select a case as test
case = c_df.loc['Mexico//']
x = case.index
y = case.values

sns.lineplot(x=x[35:],y=y[35:])
plt.xticks(rotation=90)
plt.title("Mexico")


# very crude estimation of growth rate
for i in range(len(case)):
    if case[i-1] == 0:
        continue
    else:
        print float(case[i])/float(case[i-1])

print case.pct_change()
### TO DO: IMPLEMENT SELECTING 2 CASES, FORMATTING THEM LONGFORM
### (https://github.com/mwaskom/seaborn-data/blob/master/fmri.csv)
### AND PLOTTING THEM COMPARATIVELY