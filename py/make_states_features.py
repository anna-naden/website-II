""" Read states json and replace density property with deaths in last month
"""

from get_world_covid_jh import get_world_covid_jh
from state_population_fips import state_population_fips
from push_states_features import push_states_features
from state_name_from_fips import state_name_from_fips
from get_config import get_config
from s3_util import upload_file
from csv_util import csv_get_dict, csv_lookup

import numpy as np
import json
import pandas as pd
import  os

def make_features():
    status, df = get_world_covid_jh()
    df_us = df[df.index.get_level_values('ISO_A3')=='USA']
    df_can = df[df.index.get_level_values('ISO_A3') == 'CAN']
    df.reset_index(inplace=True)
    end_date = df.date.max()
    start_date = end_date-np.timedelta64(30,'D')
    print(f'states features date range {start_date} {end_date}')
    state_deaths = {}
    
    #USA
    ISO_A3='USA'
    fips_codes = df_us.state_fips.unique()
    df=df_us.groupby(axis='index', by=['state','date']).sum()
    df.reset_index(inplace=True)
    state_pops_dict = csv_get_dict(config['FILES']['state_census'],0,1)
    for fips_code in fips_codes:

        # The Johns Hopkins data has incorrect FIPS code for unassigned county in Illinois, so instead of keying on FIPS I must key on state name, e.g. Illinois
        state_name = state_name_from_fips(fips_code)
        if state_name is not None:
            deaths1 = df.query('date==@start_date and state==@state_name').deaths.sum()
            deaths2 = df.query('date==@end_date and state==@state_name').deaths.sum()
            deaths = deaths2-deaths1
            pop = int(state_pops_dict[state_name])
            state_deaths[ISO_A3 + fips_code]=100000*deaths/pop

    # Write csv file for barcharts
    make_csv_bar_charts(state_deaths)

    #Canada
    ISO_A3 = 'CAN'
    df=df_can.groupby(axis='index', by=['state_fips','date']).sum()
    df.reset_index(inplace=True)
    canada_pop_dict = csv_get_dict(config['FILES']['canada_census'],0,1)
    fips_codes = df['state_fips'].unique()
    for fips_code in fips_codes:
        deaths1 = df.query('date==@start_date and state_fips==@fips_code').deaths.sum()
        deaths2 = df.query('date==@end_date and state_fips==@fips_code').deaths.sum()
        deaths = deaths2-deaths1
        if fips_code in canada_pop_dict.keys():
            pop = int(canada_pop_dict[fips_code])
            state_deaths[ISO_A3 + fips_code]=100000*deaths/pop
        else:
                state_deaths[ISO_A3 + fips_code] = 0
        
    with open(config['FILES']['states_geometry'], 'r') as f_usa:
        obj_us = json.load(f_usa)
    with open(config['FILES']['canada_geometry'], 'r') as f_can:
        obj_can = json.load(f_can)

    for feature in obj_us['features']:
        fid = 'USA' + feature['id']
        if fid in state_deaths.keys():
            feature['id'] = fid
            deaths = state_deaths[feature['id']]
            feature['properties']['density'] = f'{deaths}'

    features = obj_can['features']
    features2 = []
    for feature in features:
        if feature['properties']['name'] != 'Nunavut' and feature['properties']['name'] != 'Yukon Territory':    #Nunavit region
            features2.append(feature)
    obj_can['features'] = features2
    province_dict = csv_get_dict(config['FILES']['canada_census'],2,0)
    for feature in obj_can['features']:
        name = feature['properties']['name']
        id = province_dict[name]
        feature['id'] = 'CAN' + id
        deaths = state_deaths[feature['id']]
        feature['properties']['density'] = f'{deaths}'

    obj = obj_us
    obj['features'] = obj_us['features'] + obj_can['features']

    return obj

def make_csv_bar_charts(state_deaths):
    config = get_config()

    path = config['FILES']['js']+'/barchart.js'
    with open(path, 'w') as f:
        f.write('var data = [\n')
        for state in state_deaths.keys():
            state_name = state_name_from_fips(state[3:])
            if state_name is not None:
                f.write('{\n')
                f.write(f'"name": "{state_name}",\n')
                f.write(f'"value": {state_deaths[state]},\n')
                f.write('},\n')
        f.write('];')
    f.close()

config = get_config()
covid = make_features()
with open(config['FILES']['scratch'], 'w') as f:
    json.dump(covid,f)
upload_file(config['FILES']['scratch'], 'phoenix-technical-services.com', 'all-states.json', title='all-states.json')
os.remove(config['FILES']['scratch'])