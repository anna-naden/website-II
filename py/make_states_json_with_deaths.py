""" Read states json and replace density property with deaths in last month
"""

from get_world_covid_jh import get_world_covid_jh
from state_population_fips import state_population_fips
from push_states_json_with_deaths import push_states_json_with_deaths

import numpy as np
import json

def make_json():
    status, df = get_world_covid_jh()
    df = df[df.index.get_level_values('ISO_A3')=='USA']
    df=df.groupby(axis='index', by=['fips','date']).sum()
    df.reset_index(inplace=True)
    end_date = df.date.max()
    start_date = end_date-np.timedelta64(30,'D')
    fips_codes = df.fips.unique()
    state_deaths = {}
    for fips_code in fips_codes:
        deaths1 = df.query('date==@start_date and fips==@fips_code').deaths.sum()
        deaths2 = df.query('date==@end_date and fips==@fips_code').deaths.sum()
        deaths = deaths2-deaths1
        pop = state_population_fips(fips_code)
        if pop != 0:
            state_deaths[fips_code]=100000*deaths/pop
        else:
            state_deaths[fips_code] = 0
            
    with open('/home/anna_user2/projects/website-II/json/states-geometry.json') as f:
        obj = json.load(f)
    for feature in obj['features']:
        deaths = state_deaths[feature['id']]
        feature['properties']['density'] = f'{deaths}'
    with open('/home/anna_user2/projects/website-II/json/state-month-deaths.json', 'wt') as f:
        json.dump(obj,f)

make_json()
push_states_json_with_deaths()