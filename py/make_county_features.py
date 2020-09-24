import boto3
import numpy as np
import json

from county_pops_fips import county_pops_fips
from get_world_covid_jh import get_world_covid_jh

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
        print(fips_code)
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
    features2 = []
    for feature in features:
        feature['properties']['name'] = feature['properties']['county'] + ' County'
        # if feature['properties']['FIPS-code'] in ['01','02','04','05','06']:
        #     features2.append(feature) 
        features2.append(feature)
    return features2

def update_county_features(features, deaths):
    for feature in features:
        id = feature['properties']['FIPS-code'] +  feature['properties']['COUNTY']
        feature['id'] = id
        deaths1 = 0
        if id in deaths.keys():
            deaths1 = deaths[id]
        feature['properties']['density'] = f'{deaths1}'
    return features

table_name = 'counties_with_deaths'
dynamodb=boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

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
print(f'date range {start_date} {end_date}')
county_deaths = get_county_deaths(df, df_pops, start_date, end_date)
features = get_counties_features()
update_county_features(features, county_deaths)
with open('temp.json', 'w') as f:
    json.dump(features, f)
#Convert numbers to strings to satisfy DynamoDB
for feature in features:
    coordinates = feature['geometry']['coordinates']
    map_type = feature['geometry']['type']
    if map_type == 'MultiPolygon':
        coordinates = stringify_deep_multi_poly(feature['geometry']['coordinates'])
    else:
        coordinates = stringify_deep_poly(feature['geometry']['coordinates'])
    feature['geometry']['coordinates'] = coordinates
    feature['properties']['CENSUSAREA'] = stringify(feature['properties']['CENSUSAREA'])

with open('../json/temp_county.json', 'w') as f:
    json.dump(features, f)

# for feature in features:
#     fips = feature['id']
#     print('writing dynamodb: ' + fips)
#     # with open('temp.json','w') as f:
#     #     json.dump(feature, f)
#     response = table.put_item(
#         Item = {
#             'state_fips': fips[:2],
#             'county_fips': fips[2:],
#             'feature': feature,
#             'supplemental': {}
#         }
#     )
