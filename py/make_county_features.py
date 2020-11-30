"""Make JSON strings for leaflet choropleth maps and d3 graphs of
monthly COVID deaths by county. Upload to S3

"""

import boto3
import os

import numpy as np
import json
import pandas as pd
import csv

from s3_util import *
from county_pops_fips import county_pops_fips
from get_world_covid_jh import get_world_covid_jh
from get_config import get_config

def make_dict_county_graph(df1, pop, fips, start_date, end_date):
    """ Make dictionary for Javascript object to drive county d3 graph

    Args:
        df1 (DataFrame): dates and deaths for county
        pop (int): population of county
        fips (str): identifier for county
        start_date (Pandas timestamp) the start of the interval over which deaths are summed
        end_date

    Returns:
        [dictionary) corresponds to Javascript object that d3 will use to make graph
    """

    df = df1.copy()[['date','deaths']]
    df.deaths *= 100000/pop

    jsonstr = df.to_json(orient='records')
    stats = json.loads(jsonstr)
    config = get_config()
    path = config['FILES']['counties_states']

    try:
        df = pd.read_csv(path, dtype={'FIPS':str, 'county':str, 'state_abbr':str, 'state': str})
    except Exception as inst:
        return f'Exception reading {path} {inst})', None
    df = df[df.FIPS==fips]
    if not df.empty:
        start_date = format(start_date,"%x")
        end_date = format(end_date,"%x")
        county_state = df.iloc[0].county + ' County, ' + df.iloc[0].state_abbr
        dict_cty_graph = {"start_date": start_date, "end_date": end_date, "county": county_state, "stats": stats}

        return None, dict_cty_graph
    return None, None

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

# ----------------------------------------------------------
# Main
# ----------------------------------------------------------
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
    exit(1)

# County time series
df_time_series = df[['fips','date','deaths']]
df_time_series = df_time_series[df_time_series.date>=start_date_graph]
df_time_series = df_time_series[df_time_series.date<=end_date]
all_json = '{'
first=True
all_counties = {}
for county_fips in df.fips.unique():
    # print(county_fips)
    df_county_p = df_pops[df_pops.fips == county_fips]
    df_county = df_time_series[df_time_series.fips == county_fips]
    if not df_county.empty and not df_county_p.empty:
        # delete_obj('covid.phoenix-technical-services.com', county_fips + '.json')
        pop = df_county_p.population.iloc[0]
        status, county_time_series = make_dict_county_graph(df_county, pop, county_fips, start_date_graph, end_date)
        if status is not None:
            print(f'{status} from get_cty_time_series')
            exit(1 )
        if county_time_series is not None:
            all_counties.__setitem__(county_fips, county_time_series)
            # with open('temp.json', 'w') as f:
            #     json.dump(county_time_series, f)
print("Dumping all counties time series to file")
with open(config['FILES']['scratch'], 'w') as f:
    json.dump(all_counties, f)
upload_file(config['FILES']['scratch'], 'covid.phoenix-technical-services.com', 'all_counties.json')
os.remove(config['FILES']['scratch'])

#--------------------------------------------------------------------------
# County 30 day fatalities
#--------------------------------------------------------------------------
print('making and uploading county 30 day fatalities')
county_deaths = get_county_deaths(df, df_pops, start_date, end_date)
deaths_by_state = get_counties_features()
update_county_features(deaths_by_state, county_deaths)

#upload
for state in deaths_by_state.keys():
    with open(config['FILES']['scratch'], 'w') as f:
        feature_set = {'type': 'FeatureCollection', 'features': deaths_by_state[state]}
        interval = f'{w_start_date},{w_end_date}'
        feature_obj = { 'interval': interval, 'feature_set': feature_set}
        json.dump(feature_set,f)
        f.flush()
        upload_file(config['FILES']['scratch'], 'covid.phoenix-technical-services.com', state+'.json', title=state)
        os.remove(config['FILES']['scratch'])
    f.close()
print(f'\nuploaded county 30 day fatalties {start_date} to {end_date}')
