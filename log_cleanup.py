import os

import pandas as pd

logs = os.listdir('logs')
all_logs = []

for log in logs:
    if log == '.gitignore':
        continue
    df = pd.read_csv(f'logs/{log}', index_col=0)
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Datetime'}, inplace=True)
    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%d-%m-%Y %H:%M:%S.%f')
    df.sort_values(by=['Datetime'], inplace=True)
    df.reset_index(inplace=True)
    df.drop('index', inplace=True, axis=1)
    all_logs.append(df)