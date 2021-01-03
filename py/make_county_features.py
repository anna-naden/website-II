"""Make JSON strings for leaflet choropleth maps and d3 graphs of
monthly COVID deaths by county. Upload to S3

"""

import os

import numpy as np
import json
import pandas as pd
import csv
import time
import datetime
from filelock import FileLock

from send_content import send_content
from get_world_covid_jh import get_world_covid_jh
from get_config import get_config


def get_counties_features():
    config = get_config()
    with open(config['FILES']['county_coords'], 'r') as f:
        features = json.load(f)
    features = features['features']
    states = {}
    for feature in features:
        state_fips = feature['properties']['STATE']
        if state_fips not in states:
            states[state_fips] = []
    for feature in features:
        state_fips = feature['properties']['STATE']
        feature['properties']['name'] = feature['properties']['NAME'] + ' County'
        states[state_fips].append(feature)
    return states

def get_county_deaths(df_us, start_date, end_date, ndays_map):
    df_pops = df_us[['fips','population']].drop_duplicates()
    fips_codes = df_us.fips.unique()
    county_deaths = {}
    n_deaths = {}
    df1 = df_us[df_us.date == start_date]
    df2 = df_us[df_us.date == end_date]
    for fips_code in fips_codes:
        # print(fips_code)
        pop = df_pops[df_pops.fips == fips_code].population.iloc[0]
        deaths1 = df1.query('fips==@fips_code').deaths.sum()
        deaths2 = df2.query('fips==@fips_code').deaths.sum()
        deaths = deaths2 - deaths1
        if pop != 0:
            n_deaths[fips_code] = deaths
            deaths = 100000*deaths/pop
            county_deaths[fips_code] = deaths/ndays_map
    return county_deaths, n_deaths

def update_county_features(states, deaths):
    for state in states.keys():
        for feature in states[state]:
            id = feature['properties']['STATE'] +  feature['properties']['COUNTY']
            feature['id'] = id
            deaths1 = 0
            if id in deaths.keys():
                deaths1 = deaths[id]
            feature['properties']['density'] = f'{deaths1}'
    return states

# ----------------------------------------------------------
# Main
# ----------------------------------------------------------
start = time.time()
config = get_config()

status, df_world = get_world_covid_jh()
if status is not None:
    print(f'status from get_world_covid_jh: {status}')
    exit(1)

df_world1 = df_world.reset_index()
w_end_date = df_world1.date.max()
w_start_date = w_end_date-np.timedelta64(30,'D')

# Get US data file
df = df_world[df_world.index.get_level_values('ISO_A3')=='USA']
df.reset_index(inplace=True)
end_date = df.date.max()

ndays_map = int(config['MAPS']['n_days_fatalities'])
start_date = end_date-np.timedelta64(ndays_map,'D')

start_date_graph = end_date-np.timedelta64(6,"M")

#--------------------------------------------------------------------------
# County 30 day fatalities
#--------------------------------------------------------------------------
print(f'making and uploading county {ndays_map} day fatalities')
county_deaths, ndeaths = get_county_deaths(df, start_date, end_date, ndays_map)

#Collect info for markers of worst counties in the country
county_deaths_sorted = sorted(county_deaths, key=county_deaths.get, reverse=True)
n_worst = int(config['MARKERS']['n_worst_counties'])
top_deaths = county_deaths_sorted[:n_worst]
markers = {}
for key in top_deaths:
    df_cty = df[df.fips==key].iloc[0]
    lat = df_cty.latitude
    lon = df_cty.longitude
    state = df_cty.state
    cty = df_cty.county
    markers[key] = [lat, lon, state, cty]

    if config['SWITCHES']['send_content_to_local_html'] != '0':
        with open('/var/www/html/county-markers.json', 'wt') as f:
            json.dump(markers, f)
        f.close()

    lock = FileLock(config['FILES']['lockfile'])
    with lock:
        with open(config['FILES']['scratch'], 'w') as f:
            json.dump(markers, f)
        send_content(config['FILES']['scratch'], 'covid.phoenix-technical-services.com', 'county-markers.json', title='county-markers.json')
        os.remove(config['FILES']['scratch'])

# Features for each state, one feature for each county
features = get_counties_features()
update_county_features(features, county_deaths)

#upload
for state in features.keys():
    feature_set = {'type': 'FeatureCollection', 'features': features[state]}
    interval = f'{w_start_date},{w_end_date}'

    if config['SWITCHES']['send_content_to_local_html'] != '0':
        with open('/var/www/html/county-markers.json', 'wt') as f:
            json.dump(feature_set, f)
        f.close()

    lock = FileLock(config['FILES']['lockfile'])
    with lock:
        with open(config['FILES']['scratch'], 'wt') as f:
            json.dump(feature_set,f)
        f.close()
        send_content(config['FILES']['scratch'], 'covid.phoenix-technical-services.com', state+'.json', title=state+'.json')
        os.remove(config['FILES']['scratch'])
end = time.time()
seconds = round(end-start)
print(f'\nUploaded county 30 day fatalties {str(start_date)[:10]} to {str(end_date)[:10]}. Elapsed time: {str(datetime.timedelta(seconds=seconds))} seconds')
