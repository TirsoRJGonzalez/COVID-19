# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 22:24:04 2020

@author: tirso rj gonzalez alam

This script takes timeseries data forked from https://github.com/CSSEGISandData/COVID-19
and offers functionality for comparative plotting. At the moment the user can 
compare two countries' absolute or adjusted number of cases, as well as simple 
growth timeseries.

Adjusting is performed from number of tests, web-scraped from Wikipedia:
https://en.wikipedia.org/wiki/Template:COVID-19_testing
And formatted into a pickled (pkl) dataframe

The scripts are provided as is, with no warranty or support and for exploratory
purposes only
"""
# Import stuff we'll need
import os
import pandas as pd
import seaborn as sns; sns.set(style="ticks")
import matplotlib.pyplot as plt
from itertools import repeat

############################# General options #################################
# Set to True if you want to print list of available countries
show_countries = False

# Select countries to compare 
case_a = 'Czechia//'
case_b = 'Slovakia//'

# If you wish to adjust all calculations normalising them per different factors
# set to true. ATM this script supports the following adjustement factors:
# "Tests" (absolute number of tests)
# "Tests per million"
# "Positive" (absolute number of positive cases)
# "Positive per thousand" (TO DO: add more sophisticated adjustement options)
adjusted = True
adj_factor = "Tests per million"

# If true, plots a comparative line plot of two countries' absolute or adjusted
# number of cases
compare = True

# Compares absolute or adjusted growth rate as a function of percent timeseries
# change. By default, compares each day to the previous day. Care must be taken
# as each country has a different onset date, and comparisons will not be
# straightforward if unadjusted to onset. ATM reccommend not to adjust
# (TO DO: think about adding detrend, add rolling window option, sync to onset)
check_growth = True

# Compares a given country to the world trends, performing inferential stats
# [Glitchy, removed at the moment, TO DO: optimize bootstrapping]
inferentials = False
    
############################ Implementation ###################################
### load data
# Change dir and load csv and pickle (encoded in 2 to maximise compatibility)
os.chdir(os.getcwd())
sitreps = os.path.join('csse_covid_19_data','csse_covid_19_time_series',
                       'time_series_covid19_confirmed_global.csv')
tests = 'TestsPerCountry.pkl'

# load the csvs to pandas df
c_df = pd.read_csv(sitreps)
t_df = pd.read_pickle(tests)

### dataframe prep
# handle nans
c_df['Province/State'] = c_df['Province/State'].fillna('')

## set place as index
# first combine the two initial columns into one (hacky, leaves r_trail of //, FIX)
c_df['Place'] = c_df['Country/Region'] + '//' + c_df['Province/State']
# now set the new column as index 
c_df.set_index('Place', inplace=True)

# drop columns we won't need
c_df.drop(['Province/State','Country/Region','Lat','Long'],axis=1,inplace=True)

# Load the cases
c_a = c_df.loc[case_a]
c_b = c_df.loc[case_b]

### Ouputs
# Print list of available countries:
if show_countries:
    for i in c_df.index:
        print i

# construct a comparative curve plotter, the sns option takes longform dfs,
# so we must change the loaded cases to a longform dataframe
if compare:
    # load case a
    a = {'Cases': list(c_a.values), 
         'Dates': list(pd.to_datetime(c_a.index.values)), 
         'Country': list(repeat(case_a, len(c_a.values)))}
    dfa = pd.DataFrame(a,columns = ['Cases','Dates','Country'])
    # load case b
    b = {'Cases': list(c_b.values),
         'Dates': list(pd.to_datetime(c_b.index.values)), 
         'Country': list(repeat(case_b, len(c_b.values)))}
    dfb = pd.DataFrame(b,columns = ['Cases','Dates','Country'])
    
    # adjust cases per specified adjustement factor
    dfa['Cases Adjusted'] = dfa.Cases/float(t_df.loc[dfa.Country[0][:-2]][adj_factor])
    dfb['Cases Adjusted'] = dfb.Cases/float(t_df.loc[dfb.Country[0][:-2]][adj_factor])
    
    # merge case a and b dataframes' into a longform df to pass to sns plotter
    df_pt = dfa.append(dfb, ignore_index=True)
    df_p = df_pt.iloc[35:]
    
    # Plot
    plt.figure()
    if adjusted:
        sns.lineplot(x='Dates',y='Cases Adjusted',hue='Country',data=df_p)
    else:
        sns.lineplot(x='Dates',y='Cases',hue='Country',data=df_p)

# very crude estimation of growth rate (divides num cases of each day
# by num cases of previous day, doesn't sync or detrend, can be improved)
if check_growth:
    # Get percentage change
    c_a_pct = c_a.pct_change().to_frame()
    c_b_pct = c_b.pct_change().to_frame()
    # add country info
    c_a_pct["Country"] = c_a_pct.columns.values[0]
    c_b_pct["Country"] = c_b_pct.columns.values[0]
    # add date info
    c_a_pct["Dates"] = pd.to_datetime(c_a_pct.index)
    c_b_pct["Dates"] = pd.to_datetime(c_b_pct.index)
    # stack them in a new dataset
    c_a_pct.rename(columns = {c_a_pct.columns.values[0]:'% of Change'},inplace = True)
    c_b_pct.rename(columns = {c_b_pct.columns.values[0]:'% of Change'},inplace = True)
    # adjust cases per specified adjustement factor (monstrously unreadable: refactor)
    c_a_pct['Growth Adjusted'] = c_a_pct['% of Change'].values/float(t_df.loc[c_a_pct.Country[0][:-2]][adj_factor])
    c_b_pct['Growth Adjusted'] = c_b_pct['% of Change'].values/float(t_df.loc[c_b_pct.Country[0][:-2]][adj_factor])
    # merge both dfs into a longform
    c_both = c_a_pct.append(c_b_pct,ignore_index=True)
    # Plot
    plt.figure()
    if adjusted:
        g = sns.lineplot(x='Dates',y='Growth Adjusted',hue='Country',data=c_both)
    else:
        g = sns.lineplot(x='Dates',y='% of Change',hue='Country',data=c_both)
    # format labels for readability
    for item in g.get_xticklabels():
        item.set_rotation(45)

if inferentials:
    # get the mean growth across countries [FIXING GLITCH]
    print ''
    
## TO DO LIST:
#    - UPGRADE WEBSCRAPING TO LIVE WIKIPEDIA TEMPLATE
#    - BUILD MODELS AND FIT GROWTH CURVES
#    - IMPROVE FUNCTIONALITY OF GROWTH COMPARISON (BARE BONES NOW)