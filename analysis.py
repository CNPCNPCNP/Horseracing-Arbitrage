import numpy as np
import pandas as pd
import os

from constants import *

bets = os.listdir('bets')
all_bets = pd.DataFrame()

for bet in bets:
    df = pd.read_csv(f'bets/{bet}', index_col=0)
    all_bets = pd.concat([all_bets, df])

all_bets = all_bets.merge(all_bets["Venue"].str.rsplit(" ", 1, expand=True).rename(columns = {0: "Venue", 1: "Race Number"}), left_index=True, right_index=True, how = 'right')
all_bets.drop(axis = 1, labels="Venue_x", inplace=True)
all_bets.rename(columns={"Venue_y": "Venue"}, inplace=True)
all_bets["Location"] = np.where(all_bets["Venue"].isin(AMERICAN_RACES), 'USA', 'AUS')
all_bets["Midpoint Percentage"] = (all_bets["Midpoint Price"] / all_bets["Price"])

all_bets.drop('Volume', inplace=True, axis=1)
all_bets.drop('Last Price', inplace=True, axis=1)
all_bets.drop('Event ID', inplace=True, axis=1)
all_bets.drop('Race Number', inplace=True, axis=1)

all_bets.reset_index(inplace=True)
all_bets = all_bets.rename(columns={'index': 'Datetime'})
all_bets['Datetime'] = all_bets['Datetime'].apply(lambda x: x.split()[0])
all_bets['Datetime'] = all_bets['Datetime'].apply(lambda x: x.split('_')[0])

all_bets.to_csv(f'analysis/results/all_bets.csv')

betfair_csvs = os.listdir('analysis')
betfair_data = pd.DataFrame()

for csv in betfair_csvs:
    if csv != 'results':
        df = pd.read_csv(f'analysis/{csv}', index_col=0)
        betfair_data = pd.concat([betfair_data, df])

betfair_data.drop('PPMIN', inplace=True, axis=1)
betfair_data.drop('PPMAX', inplace=True, axis=1)
betfair_data.drop('IPMAX', inplace=True, axis=1)
betfair_data.drop('IPMIN', inplace=True, axis=1)
betfair_data.drop('MORNINGTRADEDVOL', inplace=True, axis=1)
betfair_data.drop('MORNINGWAP', inplace=True, axis=1)
betfair_data.drop('PPWAP', inplace=True, axis=1)
betfair_data.drop('PPTRADEDVOL', inplace=True, axis=1)
betfair_data.drop('IPTRADEDVOL', inplace=True, axis=1)
betfair_data.drop('SELECTION_ID', inplace=True, axis=1)
betfair_data.drop('EVENT_NAME', inplace=True, axis=1)
betfair_data.drop('MENU_HINT', inplace=True, axis=1)

betfair_data.reset_index(inplace=True)
betfair_data.drop('EVENT_ID', inplace=True, axis=1)
betfair_data = betfair_data.replace(regex=[r'\d+\.\s'], value='')
betfair_data['EVENT_DT'] = betfair_data['EVENT_DT'].apply(lambda x: x.split()[0])

all_bets.to_csv(f'analysis/results/all_bets.csv')
betfair_data.to_csv(f'analysis/results/betfair_data.csv')

all_bets = pd.merge(all_bets, betfair_data, left_on=['Horse', 'Datetime'], right_on=['SELECTION_NAME', 'EVENT_DT'])
all_bets["Turnover"] = (all_bets["Price"] / all_bets["BSP"] * 100)
all_bets.drop('EVENT_DT', inplace=True, axis=1)
all_bets.drop('SELECTION_NAME', inplace=True, axis=1)

all_bets.to_csv(f'analysis/results/all_bets2.csv')

print(all_bets['Turnover'].mean(), len(all_bets))

recent = all_bets.loc[(all_bets['Datetime'] == '09-01-2023') | (all_bets['Datetime'] == '08-01-2023')]

adjusted_recent = recent.loc[(recent['Midpoint Percentage'] <= 0.94) & (recent['Horse'] != "Trigger")]
print(recent['Turnover'].mean(), len(recent))
print(adjusted_recent['Turnover'].mean(), len(adjusted_recent))

