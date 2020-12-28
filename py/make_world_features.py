import numpy as np
import json
import csv
import time
import datetime
import os

from get_config import get_config
from get_world_covid_jh import get_world_covid_jh
from world_populations import world_populations
from s3_util import delete_obj
from send_content import send_content

def get_world_deaths(df_world, start_date, end_date):
    """ Compute number of deaths in calendar interval for each nation of the world, including USA

    Args:
        df_world (data frame): the master data structure for COVID fatalties
        start_date (date time): the start date of the interval
        end_date : the end date of the interval

    Returns:
        (dictionary): ISO_A3 nation code -> number of deaths
    """

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
        # print(ISO_A3)
        deaths1 = df1.query('ISO_A3==@ISO_A3').deaths.sum()
        deaths2 = df2.query('ISO_A3==@ISO_A3').deaths.sum()
        deaths = deaths2 - deaths1
        pop = 0
        if ISO_A3 in pops_dict.keys():
            pop = pops_dict[ISO_A3]['population']
            deaths = 100000*deaths/pop
            nation_deaths[ISO_A3] = deaths
    return nation_deaths

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

def update_world_features(nations, deaths, ndays_map):
    for ISO_A3 in nations.keys():
        for feature in nations[ISO_A3]:
            id = feature['properties']['adm0_a3']
            feature['id'] = id
            deaths1 = 0
            if id in deaths.keys():
                deaths1 = deaths[id]
            feature['properties']['density'] = f'{deaths1/ndays_map}'
    return nations


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------
config = get_config()
start = time.time()

status, df_world = get_world_covid_jh()
if status is not None:
    print(f'status from get_world_covid_jh: {status}')
    exit(1)

df_world1 = df_world.reset_index()
w_end_date = df_world1.date.max()

n_days_map = int(config['MAPS']['n_days_fatalities_world'])
w_start_date = w_end_date-np.timedelta64(n_days_map,'D')

# Get US data file
df = df_world[df_world.index.get_level_values('ISO_A3')=='USA']
df.reset_index(inplace=True)

# Make and upload world features
world_deaths = get_world_deaths(df_world1, w_start_date, w_end_date)

#Collect info for markers of worst counties in the country
world_deaths_sorted = sorted(world_deaths, key=world_deaths.get, reverse=True)
n_worst = int(config['MARKERS']['n_worst_nations'])
top_deaths = world_deaths_sorted[:n_worst]
markers = {}
for key in top_deaths:
    df_nation = df_world1[df_world1.ISO_A3==key].iloc[0]
    lat = df_nation.lat
    lon = df_nation.lon
    markers[key] = [lat, lon]

if config['SWITCHES']['send_content_to_local_html'] != '0':
    with open('/var/www/html/world-markers.json', 'wt') as f:
        json.dump(markers, f)
    f.close()

with open(config['FILES']['scratch'], 'w') as f:
    json.dump(markers, f)
send_content(config['FILES']['scratch'], 'covid.phoenix-technical-services.com', 'world-markers.json', title='world-markers.json')


#Make map features
nations = get_world_features()
update_world_features(nations, world_deaths, n_days_map)

#for testing
# with open('test.json', 'w') as f:
#     json.dump(nations, f)

#Upload US Data
interval = f'{w_start_date},{w_end_date}'
feature_list = []
for key in nations.keys():
    feature_list.append(nations[key][0])
with open(config['FILES']['scratch'], 'w') as f:
    feature_obj = { 'interval': interval, 'type': 'FeatureCollection', 'features': feature_list}

    if config['SWITCHES']['send_content_to_local_html'] != '0':
        with open('/var/www/html/all.json', 'wt') as f:
            json.dump(feature_obj, f)
        f.close()

    with open(config['FILES']['scratch'], 'wt') as f:
        json.dump(feature_obj, f)
    f.close()
    send_content(config['FILES']['scratch'], 'covid.phoenix-technical-services.com', 'all.json', 'all.json')
os.remove(config['FILES']['scratch'])
print('world features uploaded')

seconds = round(time.time()-start)
print(f'\nWorld features made. Elapsed time: {str(datetime.timedelta(seconds = seconds))} secs')