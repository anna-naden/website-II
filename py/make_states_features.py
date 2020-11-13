""" Read states json and replace density property with deaths in last month
"""

from get_world_covid_jh import get_world_covid_jh
from state_population_fips import state_population_fips
from push_states_features import push_states_features
from state_name_from_fips import state_name_from_fips
from get_config import get_config
from s3_util import upload_file

import numpy as np
import json
import pandas as pd
import  os
from canadian_province_id import canadian_province_id

def desample(coords):
    desample_factor = 80
    if (len(coords)<160):
        return coords

    coorda = []
    for i in range(len(coords)):
        if i%desample_factor == 0:
            coorda.append(coords[i])
        i += 1
    coorda.append(coords[0])
    return coorda

def desample_deep(l):
    out=[]
    for c in l:
        out1=[]
        for c2 in c:
            out2 = []
            map1 = map(desample,c2)
            result = list(map1)
            out1.append(result)
        out.append(out1)
    return out

def stringify(num):
    return f'{num}'

def stringify_deep_poly(l):
    out=[]
    for c in l:
        out1=[]
        for c2 in c:
            map1 = map(stringify,c2)
            result = list(map1)
            out1.append(result)
        out.append(out1)
    return out

def stringify_deep_multi_poly(l):
    out=[]
    for c in l:
        out1=[]
        for c2 in c:
            out2 = []
            for c3 in c2:
                map1 = map(stringify,c3)
                result = list(map1)
                out2.append(result)
            out1.append(out2)
        out.append(out1)
    return out

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
    for fips_code in fips_codes:
        
        # The Johns Hopkins data has incorrect FIPS code for unassigned county in Illinois, so instead of keying on FIPS I must key on state name, e.g. Illinois
        state_name = state_name_from_fips(fips_code)

        deaths1 = df.query('date==@start_date and state==@state_name').deaths.sum()
        deaths2 = df.query('date==@end_date and state==@state_name').deaths.sum()
        deaths = deaths2-deaths1
        pop = state_population_fips(ISO_A3, fips_code)
        if pop != 0:
            state_deaths[ISO_A3 + fips_code]=100000*deaths/pop
        else:
            state_deaths[ISO_A3 + fips_code] = 0
    # Write csv file for barcharts
    make_csv_bar_charts(state_deaths)

    #Canada
    ISO_A3 = 'CAN'
    df=df_can.groupby(axis='index', by=['state_fips','date']).sum()
    df.reset_index(inplace=True)
    fips_codes = df['state_fips'].unique()
    for fips_code in fips_codes:
        deaths1 = df.query('date==@start_date and state_fips==@fips_code').deaths.sum()
        deaths2 = df.query('date==@end_date and state_fips==@fips_code').deaths.sum()
        deaths = deaths2-deaths1
        pop = state_population_fips(ISO_A3, fips_code)
        if pop != 0:
            state_deaths[ISO_A3 + fips_code]=100000*deaths/pop
        else:
            state_deaths[ISO_A3 + fips_code] = 0
        
    with open('/home/anna_user2/projects/website-II/json/states-geometry.json') as f_usa:
        obj_us = json.load(f_usa)
    with open('/home/anna_user2/datasets/geography/canada.json') as f_can:
        obj_can = json.load(f_can)

    for feature in obj_us['features']:
        feature['id'] = 'USA' + feature['id']
        deaths = state_deaths[feature['id']]
        feature['properties']['density'] = f'{deaths}'

        map_type = feature['geometry']['type']
        if map_type == 'MultiPolygon':
            coordinates = stringify_deep_multi_poly(feature['geometry']['coordinates'])
        else:
            coordinates = stringify_deep_poly(feature['geometry']['coordinates'])

        feature['geometry']['coordinates'] = coordinates
    
    features = obj_can['features']
    features2 = []
    for feature in features:
        if feature['properties']['name'] != 'Nunavut' and feature['properties']['name'] != 'Yukon Territory':    #Nunavit region
            features2.append(feature)
    obj_can['features'] = features2
    for feature in obj_can['features']:
        name = feature['properties']['name']
        id = canadian_province_id(name)
        feature['id'] = 'CAN' + id
        deaths = state_deaths[feature['id']]
        feature['properties']['density'] = f'{deaths}'
        coordinates = desample_deep(feature['geometry']['coordinates'])

        map_type = feature['geometry']['type']
        if map_type == 'MultiPolygon':
            coordinates = stringify_deep_multi_poly(feature['geometry']['coordinates'])
        else:
            coordinates = stringify_deep_poly(feature['geometry']['coordinates'])

        cart = feature['properties']['cartodb_id']
        feature['properties']['cartodb_id'] = f'{cart}'
        feature['geometry']['coordinates'] = coordinates

    obj = obj_us
    obj['features'] = obj_us['features'] + obj_can['features']

    # json_str = json.dumps(obj)
    # with open('/home/anna_user2/projects/website-II/json/state-month-deaths.json', 'wt') as f:
    #     f.write(json_str)
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

# print("pushing states features")
# push_states_features(covid)
# print("states features pushed")