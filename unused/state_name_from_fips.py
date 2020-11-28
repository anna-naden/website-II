from csv import reader
from get_config import get_config

def state_name_from_fips(fips):

    config = get_config()
    with open(config['FILES']['state_fips'], 'r') as f:
        csv_reader = reader(f)
        state = 'XXX'
        for row in csv_reader:
            # row variable is a list that represents a row in csv
            if row[1]==fips:
                state = row[0]
    if state == 'XXX':
        return None
    return state
