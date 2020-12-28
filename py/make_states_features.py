""" This standalone program creates and uploads json file for choropleth map of us and Canada, placing period fatalities in the "density"
feature.  
"""

from get_world_covid_jh import get_world_covid_jh
from get_config import get_config
from send_content import send_content
from csv_util import csv_get_dict, csv_lookup

import numpy as np
import json
import  os
import time
import datetime

def make_features():
    """Read us and canada covid data frame, and the map feature json for these countries. Fill in period deaths in "density" feature.

    Returns:
        Dictionary of choropleth features
    """
    status, df = get_world_covid_jh()
    df_us = df[df.index.get_level_values('ISO_A3')=='USA']
    df_can = df[df.index.get_level_values('ISO_A3') == 'CAN']
    df.reset_index(inplace=True)
    end_date = df.date.max()

    n_days_map = int(config['MAPS']['n_days_fatalities'])
    start_date = end_date-np.timedelta64(n_days_map,'D')
    print(f'states features date range {str(start_date)[:10]} {str(end_date)[:10]}')
    state_deaths = {}
    
    #USA
    ISO_A3='USA'
    fips_codes = df_us.state_fips.unique()
    df=df_us.groupby(axis='index', by=['state','date']).sum()
    df.reset_index(inplace=True)
    state_pops_dict = csv_get_dict(config['FILES']['state_census'],0,1)
    assert(type(state_pops_dict == type({})))
    state_name_dict = csv_get_dict(config['FILES']['state_fips'], 2, 0)
    assert(type(state_name_dict) == type({}))
    for fips_code in fips_codes:

        # The Johns Hopkins data has incorrect FIPS code for unassigned county in Illinois, so instead of keying on FIPS I must key on state name, e.g. Illinois
        if fips_code in state_name_dict.keys():
            state_name = state_name_dict[fips_code]
            # print(state_name)
            deaths1 = df.query('date==@start_date and state==@state_name').deaths.sum()
            deaths2 = df.query('date==@end_date and state==@state_name').deaths.sum()
            deaths = deaths2-deaths1
            pop = int(state_pops_dict[state_name])
            state_deaths[ISO_A3 + fips_code]=100000*deaths/(pop*n_days_map)

    # Write csv file forgi barcharts
    # make_csv_bar_charts(state_deaths)

    #Canada
    ISO_A3 = 'CAN'
    df=df_can.groupby(axis='index', by=['state_fips','date']).sum()
    df.reset_index(inplace=True)
    canada_pop_dict = csv_get_dict(config['FILES']['canada_census'],1,2)
    fips_codes = df['state_fips'].unique()
    for fips_code in fips_codes:
        if fips_code == '35':
            print('hello')
        deaths1 = df.query('date==@start_date and state_fips==@fips_code').deaths.sum()
        deaths2 = df.query('date==@end_date and state_fips==@fips_code').deaths.sum()
        deaths = deaths2-deaths1
        if fips_code in canada_pop_dict.keys():
            # print(fips_code)
            pop = int(canada_pop_dict[fips_code])
            state_deaths[ISO_A3 + fips_code]=100000*deaths/(n_days_map*pop)
        else:
            state_deaths[ISO_A3 + fips_code] = 0
        
    with open(config['FILES']['states_geometry'], 'r') as f_usa:
        us_feature_dict = json.load(f_usa)
    with open(config['FILES']['canada_geometry'], 'r') as f_can:
        canada_feature_dict = json.load(f_can)

    for feature in us_feature_dict['features']:
        fid = 'USA' + feature['properties']['STATE']
        if fid in state_deaths.keys():
            feature['id'] = fid
            deaths = state_deaths[feature['id']]
            feature['properties']['density'] = f'{deaths}'
            feature['properties']['fips'] = fid

    features = canada_feature_dict['features']
    features2 = []
    for feature in features:
        if feature['properties']['name'] != 'Nunavut' and feature['properties']['name'] != 'Yukon Territory':    #Nunavit region
            features2.append(feature)
    canada_feature_dict['features'] = features2
    province_dict = csv_get_dict(config['FILES']['canada_census'], 0,1)
    for feature in canada_feature_dict['features']:
        name = feature['properties']['name']
        id = province_dict[name]
        feature['id'] = 'CAN' + id
        deaths = state_deaths[feature['id']]
        print(name, deaths)
        feature['properties']['density'] = f'{deaths}'
        feature['properties']['fips'] = 'CAN' + id

    feature_dict = us_feature_dict
    feature_dict['features'] = us_feature_dict['features'] + canada_feature_dict['features']

    return feature_dict

start = time.time()

config = get_config()
map_features = make_features()

if config['SWITCHES']['send_content_to_local_html'] != '0':
    with open('/var/www/html/all-states.json', 'wt') as f:
        json.dump(map_features, f)
    f.close()

with open(config['FILES']['scratch'], 'w') as f:
    json.dump(map_features,f)
send_content(config['FILES']['scratch'], 'covid.phoenix-technical-services.com', 'all-states.json', title='all-states.json')
os.remove(config['FILES']['scratch'])

end = time.time()
seconds = round(end-start,1)
print(f'\nStates features made. Elapsed time {seconds:0.1f} secs')