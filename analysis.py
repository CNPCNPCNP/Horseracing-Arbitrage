import numpy as np
import pandas as pd
import os

from constants import *

files = os.listdir('bets')
all_bets = pd.DataFrame()

for file in files:
    df = pd.read_csv(f'bets/{file}', index_col=0)
    all_bets = pd.concat([all_bets, df])

all_bets = all_bets.merge(all_bets["Venue"].str.rsplit(" ", 1, expand=True).rename(columns = {0: "Venue", 1: "Race Number"}), left_index=True, right_index=True, how = 'right')
all_bets.drop(axis = 1, labels="Venue_x", inplace=True)
all_bets.rename(columns={"Venue_y": "Venue"}, inplace=True)
all_bets["Location"] = np.where(all_bets["Venue"].isin(AMERICAN_RACES), 'USA', 'AUS')
all_bets["Fluc Direction"] = np.where(all_bets["Last Price"] >= all_bets["Price"], 'IN', 'OUT')
all_bets["Midpoint Percentage"] = (all_bets["Midpoint Price"] / all_bets["Price"])

all_bets.to_csv(f'analysis/all_bets.csv')
