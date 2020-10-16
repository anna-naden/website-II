import numpy as np
import json
import csv

from s3_util import *
from get_config import get_config
from get_world_covid_jh import get_world_covid_jh
from world_populations import world_populations

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

def get_nation_time_series(df, nation_name, start_date, end_date):

    # Get population
    config = get_config()
    path = config['FILES']['world_census']
    with open(path,"r") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == nation_name:
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

    start_date = format(start_date,"%x")
    end_date = format(end_date,"%x")
    jsonstr = '{' + f'"start_date": "{start_date}", "end_date": "{end_date}", "stats":' + jsonstr + '}'

    return None, jsonstr

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

# Get US data file
df = df_world[df_world.index.get_level_values('ISO_A3')=='USA']
df.reset_index(inplace=True)

end_date = df.date.max()
start_date = end_date-np.timedelta64(30,'D')
start_date_graph = end_date-np.timedelta64(6,"M")

# Make and upload world features
world_deaths = get_world_deaths(df_world1, w_start_date, w_end_date)
nations = get_world_features()
update_world_features(nations, world_deaths)

#for testing
# with open('test.json', 'w') as f:
#     json.dump(nations, f)

#Upload US Data
interval = f'{w_start_date},{w_end_date}'
feature_list = []
for key in nations.keys():
    feature_list.append(nations[key][0])
# feature_list = [nations['USA'][0]]
with open(config['FILES']['scratch'], 'w') as f:
    feature_obj = { 'interval': interval, 'type': 'FeatureCollection', 'features': feature_list}
    json.dump(feature_obj, f)
    f.flush()
    upload_file(config['FILES']['scratch'], 'phoenix-technical-services.com', 'all.json', 'all.json')
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
        upload_file(config['FILES']['scratch'], 'phoenix-technical-services.com', ISO_A3+'.json',title=ISO_A3)
        os.remove(config['FILES']['scratch'])

#US time series
print('making and uploading US Time series')
status, us_time_series_json = get_nation_time_series(df, 'United States', start_date_graph, end_date)
with open(config['FILES']['scratch'], 'w') as f:
    f.write(us_time_series_json)
upload_file(config['FILES']['scratch'], 'phoenix-technical-services.com','USA.json')
os.remove(config['FILES']['scratch'])

# France time series
print("Making and uploading France Time series")
df_fr = df_world[df_world.index.get_level_values('ISO_A3')=='FRA']
df_fr.reset_index(inplace=True)
status, france_ts_json = get_nation_time_series(df_fr, 'France', start_date_graph, end_date)
with open(config['FILES']['scratch'], 'w') as f:
    f.write(france_ts_json)
upload_file(config['FILES']['scratch'], 'phoenix-technical-services.com', 'FRA.json', title='FRA.json')
os.remove(config['FILES']['scratch'])

