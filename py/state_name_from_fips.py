from csv import reader

def state_name_from_fips(fips):

    with open('/home/anna_user2/datasets/census/state-fips.csv', 'r') as f:
        csv_reader = reader(f)
        state = 'XXX'
        for row in csv_reader:
            # row variable is a list that represents a row in csv
            if row[1]==fips:
                state = row[0]
    if state == 'XXX':
        return None
    return state
