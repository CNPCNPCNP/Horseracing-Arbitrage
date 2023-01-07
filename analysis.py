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

all_bets.drop('Volume', inplace=True, axis=1)
all_bets.drop('Last Price', inplace=True, axis=1)

betfair_data = betfair_data.replace(regex=[r'\d+\.\s'], value='')

print(all_bets)
print(betfair_data)

