"""Make JSON strings for monthly COVID deaths by county and by nation. Upload to S3

"""

import boto3
import logging
from botocore.exceptions import ClientError
import os
import sys
import threading

import numpy as np
import json
import pandas as pd
import csv

from county_pops_fips import county_pops_fips
from get_world_covid_jh import get_world_covid_jh
from get_config import get_config

class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()
            
def get_cty_time_series(df, df_pops, fips, start_date, end_date):

    # Select county and date range
    df = df[['fips','date','deaths']]
    df = df[df.date >= start_date]
    df = df[df.date <= end_date]
    df = df[df.fips==fips]
    df = df[['date','deaths']]
    
    pop = df_pops[df_pops.fips == fips].population.iloc[0]
    df.deaths *= 100000/pop

    jsonstr = df.to_json(orient='records')

    config = get_config()
    path = config['FILES']['counties_states']

    try:
        df = pd.read_csv(path, dtype={'FIPS':str, 'county':str, 'state_abbr':str, 'state': str})
    except Exception as inst:
        return f'Exception reading {path} {inst})', None
    df = df[df.FIPS == fips]
    start_date = format(start_date,"%x")
    end_date = format(end_date,"%x")
    county_state = df.iloc[0].county + ' County, ' + df.iloc[0].state_abbr
    jsonstr = '{' + f'"fips": {fips}, "start_date": "{start_date}", "end_date": "{end_date}", "county": "{county_state}", "stats":' + jsonstr + '}'

    return None, jsonstr


def get_us_time_series(df, start_date, end_date):

    # Get population
    config = get_config()
    path = config['FILES']['world_census']
    with open(path,"r") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'United States':
                pop = int(row[2])
                break;

    # Select county and date range
    df = df[df.date >= start_date]
    df = df[df.date <= end_date]
    df = df[['date','deaths']]
    df = df.groupby('date').deaths.sum().reset_index()
    df.deaths *= 100000/pop
    jsonstr = df.to_json(orient='records')

    config = get_config()
    path = config['FILES']['counties_states']

    start_date = format(start_date,"%x")
    end_date = format(end_date,"%x")
    jsonstr = '{' + f'"start_date": "{start_date}", "end_date": "{end_date}", "stats":' + jsonstr + '}'

    return None, jsonstr


def world_populations():
    """
    Get a dictionary of world populations keyed by nation code
    Returns: Keys are nation codes. Values are individual dictionaries of 'populatin' --> integer population

    >>> status, df = world_populations()
    >>> status
    >>> df['EGY']['population']
    98423595
    """

    config = get_config()
    path = config['FILES']['world_census']
    try:
        df = pd.read_csv(path, usecols=('Country Name', 'Country Code', 'population'), index_col='Country Code', \
            header=0, dtype={'Country Name': str, 'Country Code': str, 'population': int})
    except Exception as inst:
        return inst, None
    df.rename(columns={'Country Name': 'country_name'}, inplace=True)
    df.index.name='country_code'
    df.drop(inplace=True,axis='columns',labels='country_name')
    return None, df.to_dict(orient='index')

def get_county_deaths(df_us, df_pops, start_date, end_date):
    fips_codes = df_us.fips.unique()
    county_deaths = {}
    df1 = df_us[df_us.date == start_date]
    df2 = df_us[df_us.date == end_date]
    for fips_code in fips_codes:
        # print(fips_code)
        deaths1 = df1.query('fips==@fips_code').deaths.sum()
        deaths2 = df2.query('fips==@fips_code').deaths.sum()
        deaths = deaths2 - deaths1
        df = df_pops[df_pops.fips == fips_code]
        if not df.empty:
            pop = df.population.iloc[0]
            deaths = 100000*deaths/pop
            county_deaths[fips_code] = deaths
    return county_deaths

def get_world_deaths(df_world, start_date, end_date):
    ISO_A3_codes = df_world.ISO_A3.unique()
    try:
        status, pops_dict = world_populations()
        assert(status is None)
    except Exception as inst:
        return inst, None

    nation_deaths = {}
    df1 = df_world[df_world.date == start_date]
    df2 = df_world[df_world.date == end_date]
    for ISO_A3 in ISO_A3_codes:
        print(ISO_A3)
        deaths1 = df1.query('ISO_A3==@ISO_A3').deaths.sum()
        deaths2 = df2.query('ISO_A3==@ISO_A3').deaths.sum()
        deaths = deaths2 - deaths1
        pop = 0
        if ISO_A3 in pops_dict.keys():
            pop = pops_dict[ISO_A3]['population']
            deaths = 100000*deaths/pop
            nation_deaths[ISO_A3] = deaths
    return nation_deaths

def get_counties_features():
    config = get_config()
    with open(config['FILES']['county_coords'], 'r') as f:
        features = json.load(f)
    features = features['features']
    states = {}
    for feature in features:
        state_fips = feature['properties']['FIPS-code']
        if state_fips not in states:
            states[state_fips] = []
    for feature in features:
        state_fips = feature['properties']['FIPS-code']
        feature['properties']['name'] = feature['properties']['county'] + ' County'
        states[state_fips].append(feature)
    return states

def get_world_features():
    config = get_config()
    with open(config['FILES']['nation_coords577'], 'r') as f:
        features = json.load(f)
    features = features['features']
    nations = {}
    for feature in features:
        ISO_A3 = feature['properties']['adm0_a3']
        if ISO_A3 not in nations:
            nations[ISO_A3] = []
    for feature in features:
        ISO_A3 = feature['properties']['adm0_a3']
        feature['properties']['name'] = feature['properties']['admin']
        nations[ISO_A3].append(feature)
    return nations

def update_county_features(states, deaths):
    for state in states.keys():
        for feature in states[state]:
            id = feature['properties']['FIPS-code'] +  feature['properties']['COUNTY']
            feature['id'] = id
            deaths1 = 0
            if id in deaths.keys():
                deaths1 = deaths[id]
            feature['properties']['density'] = f'{deaths1}'
    return states

def update_world_features(nations, deaths):
    for ISO_A3 in nations.keys():
        for feature in nations[ISO_A3]:
            id = feature['properties']['adm0_a3']
            feature['id'] = id
            deaths1 = 0
            if id in deaths.keys():
                deaths1 = deaths[id]
            feature['properties']['density'] = f'{deaths1}'
    return nations

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name, Callback=ProgressPercentage(file_name))
    except ClientError as e:
        logging.error(e)
        return False
    return True

# ----------------------------------------------------------
# Main
# ----------------------------------------------------------
config = get_config()

status, df_world = get_world_covid_jh()
if status is not None:
    print(f'status from get_world_covid_jh: {status}')
    exit()

df_world1 = df_world.reset_index()
w_end_date = df_world1.date.max()
w_start_date = w_end_date-np.timedelta64(30,'D')

# Make and upload world features
world_deaths = get_world_deaths(df_world1, w_start_date, w_end_date)
nations = get_world_features()
update_world_features(nations, world_deaths)

#for testing
# with open('test.json', 'w') as f:
#     json.dump(nations, f)

#Upload
interval = f'{w_start_date},{w_end_date}'
feature_list = []
for key in nations.keys():
    f = nations[key][0]
    feature_list.append(f)
with open(config['FILES']['scratch'], 'w') as f:
    feature_obj = { 'interval': interval, 'type': 'FeatureCollection', 'features': feature_list}
    json.dump(feature_obj, f)
    f.flush()
    upload_file(config['FILES']['scratch'], 'phoenix-technical-services.com', 'all.json')
    f.close()
os.remove(config['FILES']['scratch'])
print('world features uploaded')

if False:
    print('uploading individual countries')
    for ISO_A3 in nations.keys():
        print(ISO_A3)
        with open(config['FILES']['scratch'], 'w') as f:
            feature_set = {'type': 'FeatureCollection', 'features': nations[ISO_A3]}
            feature_obj = { 'interval': interval, 'feature_set': feature_set}
            json.dump(feature_obj, f)
            f.flush()
        f.close()
        upload_file(config['FILES']['scratch'], 'phoenix-technical-services.com', ISO_A3+'.json')
        os.remove(config['FILES']['scratch'])

# Get master data file
df = df_world[df_world.index.get_level_values('ISO_A3')=='USA']
df.reset_index(inplace=True)
end_date = df.date.max()
start_date = end_date-np.timedelta64(30,'D')
start_date_graph = end_date-np.timedelta64(6,"M")

# -------------------------------------------------------
# Make and upload county six-month stats
# -------------------------------------------------------
status, df_pops = county_pops_fips()

# Get population
pops_dict = df_pops.to_dict(orient='dict')
df_pops['fips'] = df_pops.state_fips + df_pops.county_fips
df_pops.drop(columns=['state_fips', 'county_fips', 'state', 'county'], inplace=True)
if status is not None:
    print(f'status from county_pops_fips: {status}')
    exit()

status, county_time_series_json = get_cty_time_series(df, df_pops, '17031', start_date_graph, end_date)
if status is not None:
    print(f'{status} from get_cty_time_series')
    exit(0)

# County time series
with open(config['FILES']['scratch'], 'w') as f:
    f.write(county_time_series_json)
upload_file(config['FILES']['scratch'], 'phoenix-technical-services.com', 'cty-time-series.json')
os.remove(config['FILES']['scratch'])

#US time series
status, us_time_series_json = get_us_time_series(df, start_date_graph, end_date)
with open(config['FILES']['scratch'], 'w') as f:
    f.write(us_time_series_json)
upload_file(config['FILES']['scratch'], 'phoenix-technical-services.com','us-time-series.json')
os.remove(config['FILES']['scratch'])

#--------------------------------------------------------------------------
# County 30 day fatalities
#--------------------------------------------------------------------------
county_deaths = get_county_deaths(df, df_pops, start_date, end_date)
states = get_counties_features()
update_county_features(states, county_deaths)

#upload
for state in states.keys():
    # print(state)
    with open(config['FILES']['scratch'], 'w') as f:
        feature_set = {'type': 'FeatureCollection', 'features': states[state]}
        interval = f'{w_start_date},{w_end_date}'
        feature_obj = { 'interval': interval, 'feature_set': feature_set}
        json.dump(feature_set,f)
        f.flush()
        upload_file(config['FILES']['scratch'], 'phoenix-technical-services.com', state+'.json')
        os.remove(config['FILES']['scratch'])
    f.close()
print(f'\nuploaded county features {start_date} to {end_date}')
