import pandas as pd 
from csv import reader
from get_config import get_config

def canadian_province_id(name):
    config = get_config()

    with open('/home/anna_user2/datasets/census/canada/state-census.csv') as f:
        csv_reader = reader(f)
        for row in csv_reader:
            if row[2] == name:
                return row[0]
    return ''

print(canadian_province_id('British Columbia'))