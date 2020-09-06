import pandas as pd 
from csv import reader
from get_config import get_config
from df_utils import *

def state_population_fips(fips):
    config = get_config()

    with open('/home/anna_user2/datasets/census/state-fips.csv', 'r') as f:
        csv_reader = reader(f)
        state = 'XXX'
        for row in csv_reader:
            # row variable is a list that represents a row in csv
            if row[1]==fips:
                state = row[0]
    if state == 'XXX':
        return 0
    with open(config['FILES']['state_census']) as f:
        csv_reader = reader(f)
        for row in csv_reader:
            if row[0]==state:
                return int(row[1])
    return 0

print(state_population_fips('01'))