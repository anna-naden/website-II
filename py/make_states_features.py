""" Read states json and replace density property with deaths in last month
"""

from get_world_covid_jh import get_world_covid_jh
from state_population_fips import state_population_fips
from push_states_features import push_states_features

import numpy as np
import json
import pandas as pd

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
    state_deaths = {}
    
    #USA
    ISO_A3='USA'
    df=df_us.groupby(axis='index', by=['fips','date']).sum()
    df.reset_index(inplace=True)
    fips_codes = df.fips.unique()
    for fips_code in fips_codes:
        deaths1 = df.query('date==@start_date and fips==@fips_code').deaths.sum()
        deaths2 = df.query('date==@end_date and fips==@fips_code').deaths.sum()
        deaths = deaths2-deaths1
        pop = state_population_fips(ISO_A3, fips_code)
        if pop != 0:
            state_deaths[ISO_A3 + fips_code]=100000*deaths/pop
        else:
            state_deaths[ISO_A3 + fips_code] = 0
        
    #Canada
    ISO_A3 = 'CAN'
    df=df_can.groupby(axis='index', by=['fips','date']).sum()
    df.reset_index(inplace=True)
    fips_codes = df.fips.unique()
    for fips_code in fips_codes:
        deaths1 = df.query('date==@start_date and fips==@fips_code').deaths.sum()
        deaths2 = df.query('date==@end_date and fips==@fips_code').deaths.sum()
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

covid = make_features()
push_states_features(covid)