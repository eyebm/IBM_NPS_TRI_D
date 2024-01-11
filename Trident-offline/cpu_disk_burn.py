from os import sep
from datetime import datetime, date
import pandas as pd
import numpy as np


def cpu_disk_burn(data):
   
    data = data.drop(columns=['AVG_MAX_SPUCPU', 'MAX_SPU_CPU'])
    data = data.rename(columns={"?COLUMN?": "DT"})
    data['DT'] = data['DT'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    data['DOW'] = data['DT'].apply(lambda x: x.isoweekday() % 7 + 1)
    data['MONTH'] = data['DT'].apply(lambda x: str(x.month))
    data['YR'] = data['DT'].apply(lambda x: str(x.year))
    data['Counter of Hours'] = 1
    data = data[['Counter of Hours','DT', 'DOW','MONTH', 'YR', 'HR', 'AVG_SPUCPU', 'AVG_SPUDISK']]
    break_by(data, 'CPU')
    break_by(data, 'DISK')
    data = data.drop(columns=['AVG_SPUCPU', 'AVG_SPUDISK'])
    
    result = {}

    buffer = data.groupby('HR').sum().drop(columns='DOW')
    buffer = buffer.reset_index()
    result['by_hr'] = swap_cols(buffer, 'HR', 'Counter of Hours')
    
    buffer = data.groupby('DOW').sum().drop(columns='HR')
    buffer = buffer.reset_index()
    result['by_dow'] = swap_cols(buffer, 'DOW', 'Counter of Hours')

    buffer = data.groupby(['MONTH', 'YR']).sum().drop(columns=['HR', 'DOW']).sort_index()
    buffer = buffer.reset_index()
    buffer['MONTH'] = buffer['MONTH'] + "-1-" + buffer['YR']
    buffer['MONTH'] = buffer['MONTH'].apply(lambda x: datetime.strptime(x,'%m-%d-%Y'))
    buffer = buffer.sort_values(by='MONTH', ignore_index=True)
    buffer['MONTH'] = buffer['MONTH'].apply(lambda x: x.strftime('%b-%y'))
    buffer = buffer.drop(columns='YR')
    result['by_month'] = swap_cols(buffer, 'MONTH', 'Counter of Hours')

    return result

def swap_cols(df, a, b):
    cols = list(df.columns)
    aa, bb = cols.index(a), cols.index(b)
    cols[bb], cols[aa] = cols[aa], cols[bb]
    return df[cols]

def break_by(df, target):
    for i in range(1,8):
        col = target + " BURN > " + str(i*10)
        df[col] = np.where(df['AVG_SPU'+target] > i*10, 1, 0)
    



