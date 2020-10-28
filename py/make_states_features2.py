""" Read states json and add election night features
"""

from state_name_from_fips import state_name_from_fips
from get_config import get_config

import numpy as np
import json
import pandas as pd

def state_proj(id, electoral_votes):
    id = id[3:]
    state = state_name_from_fips(id)
    if state is not None:
        votes = electoral_votes[state]
        return None, {'id': state, 'votes': votes}
    return "Not found", None

def make_features2(electoral_votes):

    with open('/home/anna_user2/projects/website-II/json/states-geometry.json') as f_usa:
        obj_us = json.load(f_usa)

    total = 0
    for feature in obj_us['features']:
        feature['id'] = 'USA' + feature['id']
        status, projection = state_proj(feature['id'], electoral_votes)
        if status is None:
            total += int(projection['votes'])
            feature['properties']['proj'] = projection
    
    print(total)
    json_str = json.dumps(obj_us)
    with open('/home/anna_user2/projects/website-II/json/state-month-deaths.json', 'wt') as f:
        f.write(json_str)
    return obj_us

with open('/home/anna_user2/projects/website-II/json/electoral-votes.json', 'r') as f:
    electoral_votes = json.load(f)
proj = make_features2(electoral_votes)
# print("pushing states features 2")
# push_states_features2(covid)
# print("states features 2 pushed")