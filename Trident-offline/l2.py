import pandas as pd
import numpy as np
import l1
from datetime import datetime
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows



def top_users(df, percent: float):
    data = df.copy()
    data.drop(['DT', 'HR'], inplace=True, axis=1)

    data = data.groupby('USERNAME').aggregate(np.sum)
    data['CNT'] = data['CNT'] / data['CNT'].sum()
    data['QTIME'] = data['QTIME'] / data['QTIME'].sum()
    data['RTIME'] = data['RTIME'] / data['RTIME'].sum()
    frames = {"by_cnt": [], "by_qt": [], "by_rt": []}
    frames['by_cnt'] = top_percent(data.sort_values(['CNT'], ascending = False).reset_index(), percent, 'CNT')
    frames['by_qt'] = top_percent(data.sort_values(['QTIME'], ascending = False).reset_index(), percent, 'QTIME')
    frames['by_rt'] = top_percent(data.sort_values(['RTIME'], ascending = False).reset_index(), percent, 'RTIME')

    
    unique = get_unique_top_users(frames)
    return frames, unique
    

def top_percent(data, percent: float, key):
    result = pd.DataFrame(columns=['USERNAME', 'PERCENT'])
    count = 0.0
    i = 0
    while(count < percent):
        values = data.iloc[[i]]
        result = result.append({'USERNAME': values.at[i, 'USERNAME'], 'PERCENT': values.at[i,key]}, ignore_index=True)
        count = count + values.at[i, key]
        i+=1
    return result



def get_unique_top_users(frames):
    result = pd.merge(frames['by_cnt'], frames['by_qt'], how='outer')
    result = pd.merge(result, frames['by_rt'], how='outer')
    result = result.sort_values(by='PERCENT', ascending=False)
    result = result.drop_duplicates(subset='USERNAME', keep='first', ignore_index=True)
    return result

def process_user(df, username, months):
    
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    hrs = range(24)
    data = df[df['USERNAME'].str.fullmatch(username)].copy()
    result = {}
    
    result['hr'] = l1.process(data, 'HR')
    result['hr'] = fill_missing(result['hr'], hrs)
    result['hr'] = result['hr'].sort_values(by='HR', ignore_index=True)
    data['DT'] = data['DT'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    
    data['WEEKDAY'] = data['DT'].apply(lambda x: pd.to_datetime(x).day_name())
    week_data = data[['WEEKDAY', 'CNT', "QTIME", 'RTIME']]
    result['dow'] = l1.process(week_data, 'WEEKDAY')
    result['dow'] = fill_missing(result['dow'], days)
    result['dow'] = sort_weekday(result['dow'])

    data['MTH'] = data['DT'].apply(lambda x: x.month)
    data['YR'] = data['DT'].apply(lambda x: x.strftime("%y"))
    result['yr'] = data[['YR', 'MTH', 'CNT', 'QTIME', 'RTIME']].groupby(['YR', 'MTH']).mean().reset_index()
    result['yr']['MONTH_YR'] = result['yr']['MTH'].astype(str) + "-" + result['yr']['YR'].astype(str)
    first_col = result['yr'].pop('MONTH_YR')
    result['yr'].insert(0, 'MONTH_YR', first_col)
    result['yr'] = fill_missing(result['yr'], months)
    result['yr']['DT'] = result['yr']['MONTH_YR'].apply(lambda x: datetime.strptime(x, "%m-%y"))
    result['yr'] = result['yr'].sort_values(by='DT', ignore_index=True)
    result['yr']['MONTH_YR'] = result['yr']['DT'].apply(lambda x: x.strftime('%b-%y'))
    result['yr'].drop(columns = ['DT','YR', 'MTH'], inplace = True)
    return result

# def process_yr(day_df, yr_df):
#     day_data = l1.trim_space(day_df)
#     yr_data = l1.trim_space(yr_df)
#     days = l1.num_days(day_data)
#     hours = np.full(days.shape[0], 24)
#     hours = days['days'] * hours
#     hours.iloc[0], hours.iloc[-1]= l1.first_lasthrs(day_data)
    
#     result = yr_data.copy()
#     result.columns = [col.strip() for col in list(result.columns)]
#     result.drop(['YR', 'MTH'], inplace=True, axis=1)
#     result.insert(0, 'Month', days['DT'])
#     result['Month'] = result['Month'].apply(lambda x: str(x.month) +"/"+ str(x.year))
#     result['CNT'] = result['CNT']/hours 
#     result['QTIME'] = result['QTIME']/hours
#     result['RTIME'] = result['RTIME']/hours
#     return result

def fill_missing(d, col):
    df = d.copy()
    for key in col:
        if key not in df.iloc[:,0].tolist():
            row = pd.Series(0, index=df.columns)
            row.iloc[0] = key
            df = df.append(row, ignore_index=True)
    return df





def sort_weekday(df):
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    df['daynum'] = df['WEEKDAY'].apply(lambda x: days.index(x))
    df = df.sort_values(by='daynum', ignore_index=True)
    df = df.drop(columns='daynum')
    return df
