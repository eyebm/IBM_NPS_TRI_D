import pandas as pd
import numpy  as np
from datetime import datetime

####
# This module contains helper functions for preparing the Level 1 Tri-D Analysis, or the analysis
# for the system as a whole.
####


# The 'process' function takes input of a data frame containing the query volume, runtime, and queue times derived from
# either the hour-of-day or day-of-week tri-d outputs, as well as a key that determines whether we are grouping by the "HR" column
# or the "WEEKDAY" column. This is so that this function can be reused for both analyses as they use the same logic. It calculates
# the average of each of the three dimensions.
def process(df, key):
    data = trim_space(df)
    data = data.groupby(key).mean()
    return data.reset_index()

# The "process_yr" function does the same calculation for the month-to-month data as the previous function, but with
# some additional preprocessing of the data. We have to count how many hours are included in each month because the first and last
# months don't necessarily run for the whole month. There's also some formatting of the processed data to make it match the format
# expected by the chart-creation spreadsheets. The function takes a dataframe derived from the hour-of-day tri-d output to calculate
# how many hours are in each month, and a dataframe derived from the month-to-month data, and outputs a dataframe containing the
# hourly averages of the three dimensions for each month. We only have to calculate the average query volume, as the runtime and 
# queue time averages are calculated on collection

def process_yr(day_df, yr_df):

    #Strip whitespace out of the inputs
    day_data = trim_space(day_df)
    yr_data = trim_space(yr_df)
    #Calculate how many days of data we have for each month
    days = num_days(day_data)
    #Create a vector of 24's to multiply with the days vector to give us how many hours are in each month
    hours = np.full(days.shape[0], 24)
    hours = days['days'] * hours
    #Calculate how many hours were in the first and last months, as it will not necessarily start and end with a full day of data
    # or start at the beginnning of the month
    hours.iloc[0], hours.iloc[-1]= first_lasthrs(day_data)
    
    #Output header reformatting
    result = yr_data.copy()
    result.columns = [col.strip() for col in list(result.columns)]
    result.drop(['YR', 'MTH'], inplace=True, axis=1)
    result.insert(0, 'Month', days['DT'])
    result['Month'] = result['Month'].apply(lambda x: x.strftime('%b-%y'))
    #Calculate the average query volume
    result['CNT'] = result['CNT']/hours
    return result   

# This function calculates how many hours are in the first and last months of the analysis
    
def first_lasthrs(df):
    data = df.copy()
    #Datetime reformatting
    data['DT'] = data['DT'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    data['DT'] = data['DT'].apply(lambda x: str(x.month) +"/"+ str(x.year))
    
    
    data = data.groupby('DT')['HR'].count()
    data = data.to_frame().reset_index()
    data['DT'] = data['DT'].apply(lambda x: datetime.strptime(x, "%m/%Y"))
    data = data.sort_values('DT').reset_index(drop=True)
    data['DT'] = data['DT'].apply(lambda x: str(x.month) +"/"+ str(x.year))
    return data.iloc[0]['HR'], data.iloc[-1]['HR']

#This function calcualtes how many days of data are in each month
def num_days(df):
    data = df.copy()
    data['DT'] = data['DT'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    data = data.groupby('DT').agg('sum')
    data = data.reset_index()

    data['DT'] = data['DT'].apply(lambda x: x.replace(day=1))
    data = data['DT'].value_counts()
    data = data.reset_index()
    data = data.rename(columns={"index" : "DT", "DT": "days"})
    data = data.sort_values('DT').reset_index(drop=True)
    return data

#This function strips the whitespace out of all of the columns.    
def trim_space(df):
    data = df.copy()
    data.columns = [col.strip() for col in list(data.columns)]
    data = data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)   
    return data
