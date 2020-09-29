import boto3
import logging
from botocore.exceptions import ClientError
import os
import sys
import threading

import numpy as np
import json

from county_pops_fips import county_pops_fips
from get_world_covid_jh import get_world_covid_jh

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
            
def get_county_deaths(df_us, df_pops, start_date, end_date):
    fips_codes = df_us.fips.unique()
    df_pops['fips'] = df_pops.state_fips + df_pops.county_fips
    df_pops.set_index(keys='fips', inplace=True)
    df_pops.drop(columns=['state_fips', 'county_fips', 'state', 'county'], inplace=True)
    pops_dict = df_pops.to_dict(orient='dict')
    pops_dict = pops_dict['population']
    county_deaths = {}
    df1 = df_us[df_us.date == start_date]
    df2 = df_us[df_us.date == end_date]
    for fips_code in fips_codes:
        # print(fips_code)
        deaths1 = df1.query('fips==@fips_code').deaths.sum()
        deaths2 = df2.query('fips==@fips_code').deaths.sum()
        deaths = deaths2 - deaths1
        pop = 0
        if fips_code in pops_dict.keys():
            pop = pops_dict[fips_code]
            deaths = 100000*deaths/pop
            county_deaths[fips_code] = deaths
    return county_deaths

def get_counties_features():
    with open('/home/anna_user2/datasets/geography/county-coords.json', 'r') as f:
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
        response = s3_client.upload_file(file_name, bucket, object_name, Callback=ProgressPercentage(path+state+'.json'))
    except ClientError as e:
        logging.error(e)
        return False
    return True

make_temp_file = True
path = '/home/anna_user2/projects/website-II/json/'

if make_temp_file:
    status, df_pops = county_pops_fips()
    if status is not None:
        print(f'status from county_pops_fips: {status}')
        exit()
    status, df_world = get_world_covid_jh()
    if status is not None:
        print(f'status from get_world_covid_jh: {status}')
        exit()

    df = df_world[df_world.index.get_level_values('ISO_A3')=='USA']
    df.reset_index(inplace=True)
    end_date = df.date.max()
    start_date = end_date-np.timedelta64(30,'D')
    county_deaths = get_county_deaths(df, df_pops, start_date, end_date)
    states = get_counties_features()
    update_county_features(states, county_deaths)
    for state in states.keys():
        # print(state)
        with open(path + state + '.json', 'w') as f:
            path2 = path + state + '.json'
            feature_set = {'type': 'FeatureCollection', 'features': states[state]}
            json.dump(feature_set,f)
            f.flush()
            upload_file(path2, 'phoenix-anna-web-content', state+'.json')
        f.close()
    print(f'\nuploaded county features {start_date} to {end_date}')
