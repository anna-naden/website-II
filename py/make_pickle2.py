import datetime
import csv
import pandas as pd
import time

from get_config import get_config
from read_parse_aliases import read_parse_aliases
from csv_util import csv_get_dict

def save_keys_to_dataframes(keys_global, keys_us):
    config = get_config()

    states_of_country = {}

    canada_fips = {
        'Newfoundland and Labrador': 10,
        'Prince Edward Island': 11,
        'Nova Scotia': 12,
        'New Brunswick': 13,
        'Quebec': 24,
        'Ontario': 35,
        'Manitoba': 46,
        'Saskatchewan': 47,
        'Alberta': 48,
        'British Columbia': 59,
        'Yukon': 60,
        'Northwest Territories': 61,
        'Nunavut': 62,
        'Diamond Princess': 00,
        'Grand Princess': 00,
    }

    states=[]
    country_names = []
    lats = []
    lons = []

    ISO_A3s = []
    country_name_dict = csv_get_dict(config['FILES']['world_census'], 0,1)
    alias_dict = read_parse_aliases(config['FILES']['country_aliases'])
    keys_global2 = []
    state_fips_s = []

    for key in keys_global:
        country_name = key[1]
        if country_name in alias_dict.keys():
            country_name = alias_dict[country_name]
        if country_name != 'XXX':
            state = key[0]
            
            states.append(state)
            country_names.append(key[1])
            lats.append(key[2])
            lons.append(key[3])

            ISO_A3 = country_name_dict[country_name]

            if state != '':
                if ISO_A3 not in states_of_country.keys():
                    states_of_country[ISO_A3] = [state]
                else:
                    states_of_country[ISO_A3].append(state)

            ISO_A3s.append(ISO_A3)

            if country_name == 'Canada':
                state_fips_s.append(f'{canada_fips[key[0]]}')
            else:
                state_fips_s.append('')
            
            keys_global2.append(tuple(key[:2]))

    keys_global = keys_global2

    df_global_keys = pd.DataFrame({'key': keys_global, 'ISO_A3': ISO_A3s, 'state': states, \
        'state_fips': state_fips_s, 'country_name': country_names, 'lat': lats, 'lon': lons}).set_index('key')
    # status, df = get_world_covid_jh()

    UIDs = []
    iso2s = []
    iso3s = []
    code3s = []
    FIPs = []
    Admin2s = []
    states = []
    country_regions = []
    lats = []
    lons = []
    combined_keys = []
    populations = []

    fips_s = []
    country_names = []
    ISO_A3s = []
    counties = []
    state_fips_s = []

    keys = []
    for key in keys_us:
        UIDs.append(key[0])
        iso2s.append(key[1])
        iso3s.append(key[2])
        code3s.append(key[3])
        FIPs.append(key[4])
        Admin2s.append(key[5])
        state = key[6]
        states.append(state)
        country_regions.append(key[7])
        lats.append(key[8])
        lons.append(key[9])
        combined_keys.append(key[10])
        populations.append(key[11])

        fips_s.append(key[0][3:])
        country_names.append('USA')
        ISO_A3s.append('USA')
        counties.append(key[5])
        state_fips_s.append(key[0][3:5])

        keys.append(tuple(key[:8]))

        if state != '':
            if 'USA' not in states_of_country.keys():
                states_of_country['USA'] = [state]
            elif state not in states_of_country['USA']:
                states_of_country['USA'].append(state)

    df_us_keys = pd.DataFrame({'key' : keys, 'fips': fips_s, 'state_fips': state_fips_s, \
        'country_name': country_names, 'ISO_A3': ISO_A3s, 'county': counties, \
        'UID': UIDs, 'isos2': iso2s, 'isos3': iso3s, 'code3': code3s, \
        'FIPs': FIPs, 'Admin2': Admin2s, 'state': states, 'country_region': country_regions, 'latitude': lats, \
            'longitude': lons, 'combined_key': combined_keys, 'population': populations}).set_index('key')
    return df_global_keys, df_us_keys, states_of_country

def read_csvs():
    config = get_config()
    try:
        with open(config['FILES']['world_covid_deaths'], 'rt', newline='') as f:
            reader = csv.reader(f)
            death_lines = list(reader)
        with open(config['FILES']['world_covid_cases'], 'rt', newline='') as f:
            reader = csv.reader(f)
            cases_lines = list(reader)
        with open(config['FILES']['us_covid_deaths'], 'rt', newline='') as f:
            reader = csv.reader(f)
            us_death_lines = list(reader)
        with open(config['FILES']['us_covid_cases'], 'rt', newline='') as f: 
            reader = csv.reader(f)
            us_cases_lines = list(reader)
    except Exception as inst:
        print(inst)
        exit(1)
    
    assert (len(us_death_lines)==len(us_cases_lines))
    assert (len(cases_lines) == len(death_lines))

    return death_lines, cases_lines, us_death_lines,us_cases_lines

def get_keys(date_start_global, dd_us, dc_us, death_lines, cases_lines, us_death_lines, us_cases_lines):
    keys_global_d = []
    values_global_d = {}
    for d in death_lines:
        key = d[:date_start_global]
        keys_global_d.append(key)
        assert (tuple(key[:2]) not in values_global_d.keys())
        values_global_d[tuple(key[:2])]=d[date_start_global:]


    keys_global_c = []
    values_global_c = {}
    for c in cases_lines:
        key = c[:date_start_global]
        keys_global_c.append(key)
        assert (tuple(key[:2]) not in values_global_c.keys())
        values_global_c[tuple(key[:2])]=c[date_start_global:]
    assert (keys_global_c == keys_global_d)

    keys_us_d = []
    values_us_d = {}
    for d in us_death_lines:
        key = d[:dd_us]
        keys_us_d.append(key)
        assert (tuple(key[:8]) not in values_us_d.keys())
        # assert (tuple(key[:8]) != ('84038017', 'US', 'USA', '840', '38017.0', 'Cass', 'North Dakota', 'US'))
        values_us_d[tuple(key[:8])]=d[dd_us:]

    keys_us_c = []
    values_us_c = {}
    for c in us_cases_lines:
        key = c[:dc_us]
        keys_us_c.append(key)
        assert (tuple(key[:8]) not in values_us_c.keys())
        values_us_c[tuple(key[:8])]=c[dc_us:]

    #Compare death keys with cases keys
    assert (keys_global_c == keys_global_d)
    for i in range(len(keys_us_c)):
        for j in range(len(keys_us_c[i])):
            assert (len(keys_us_c[i])+1==len(keys_us_d[i]))
            if j != 8 and j != 9 and j != 13:
                assert (keys_us_c[i][j]==keys_us_d[i][j])

    #Now that we have verified redundancy, we no longer have to distinguish between death keys and cases keys
    keys_global = keys_global_c
    keys_us = keys_us_d
    return keys_global, keys_us, values_global_d, values_global_c, values_us_d, values_us_c

def make_pickle(keep_index = True):
    """[summary]

    Args:
        keep_index (bool, optional): Whether to keep data columns as index levels. Defaults to False.

    Returns:
        DataFrame: Indexed by ISO-A3 nation code, common names of state and country, plus date. Columns are cases and fatalities

    >>> status, df = make_pickle()
    >>> status
    >>> df = df[df.index.get_level_values('ISO_A3')=='MEX']
    >>> df = df[df.index.get_level_values('date') == '2020-04-10']
    >>> get_value_by_col(df, 'cases')
    3844
    >>> get_value_by_col(df, 'deaths')
    233
    >>> status, df = make_pickle()
    >>> status
    >>> df = df[df.index.get_level_values('ISO_A3')=='USA']
    >>> get_value_by_date_col(df, '2020-04-10', 'cases')
    497943
    >>> get_value_by_date_col(df, '2020-04-10', 'deaths')
    23362
    """
    config = get_config()

    start = time.time()
    death_lines, cases_lines, us_death_lines,us_cases_lines = read_csvs()
    end = time.time()
    print(f'read_csvs {end-start}')

    start = time.time()
    for d in us_death_lines:
        key = d[:12]
        # assert (tuple(key[:8]) != ('84038001', 'US', 'USA', '840', '38001.0', 'Adams', 'North Dakota', 'US'))

    d_header = death_lines.pop(0)
    d_us_header = us_death_lines.pop(0)
    c_header = cases_lines.pop(0)
    c_us_header = us_cases_lines.pop(0)
    assert (d_header == c_header)

    # Where the date info starts
    date_start_global = d_header.index('Long') + 1
    dd_us = d_us_header.index('Population') + 1
    dc_us = c_us_header.index('Combined_Key') + 1
    assert (d_header[date_start_global:]==d_us_header[dd_us:])
    assert (d_us_header[dd_us:]== c_header[date_start_global:])
    assert (c_header[date_start_global:]==c_us_header[dc_us:])
    dates = d_header[date_start_global:]

    end = time.time()
    print(f'first block {end-start}')

    #Separate keys from values
    start = time.time()

    keys_global, keys_us, values_global_d, values_global_c, values_us_d, values_us_c = \
        get_keys(date_start_global, dd_us, dc_us, death_lines, cases_lines, us_death_lines, us_cases_lines)
    
    end = time.time()
    print(f'get_keys {end-start}')

    #Save keys to dataframes
    start = time.time()
    df_global_keys, df_us_keys, states_of_country = save_keys_to_dataframes(keys_global, keys_us)
    end = time.time()
    print(f'save keys {end-start}')

    #Save values to dataframes
    start = time.time()

    expanded_dates = []
    expanded_keys = []
    cases = []
    deaths = []
    for key in keys_global:
        idate = 0
        for date in dates:
            expanded_dates.append(datetime.datetime.strptime(date,'%m/%d/%y'))
            expanded_keys.append(tuple(key[:2]))
            cases.append(int(values_global_c[tuple(key[:2])][idate]))
            deaths.append(int(values_global_d[tuple(key[:2])][idate]))
            idate += 1
    df_global = pd.DataFrame({'key': expanded_keys, 'date':expanded_dates, 'cases': cases, 'deaths': deaths}).set_index('key')
    end = time.time()
    print(f'making df_global {end-start}')

    start = time.time()
    expanded_dates = []
    expanded_keys = []
    cases = []
    deaths = []
    dates2=[]
    for date in dates:
        dates2.append(datetime.datetime.strptime(date,'%m/%d/%y'))
    for key in keys_us:
        tkey = tuple(key[:8])
        valuesc = values_us_c[tkey]
        valuesd = values_us_d[tkey]
        idate = 0
        for date in dates:
            expanded_dates.append(dates2[idate])
            expanded_keys.append(tkey)
            deaths1 = int(valuesd[idate])
            # assert(key[0] != '84038017' or idate != len(dates)-1)
            cases.append(int(valuesc[idate]))
            deaths.append(deaths1)
            idate += 1
    end = time.time()
    print(f'creating data structure for df_us {end-start}')

    start = time.time()
    df_us = pd.DataFrame({'key': expanded_keys, 'date':expanded_dates, 'cases': cases, 'deaths': deaths}).set_index('key')
    end = time.time()
    print(f'making df_us {end-start}')

    start = time.time()

    dfg = df_global_keys.join(df_global, on='key')
    end = time.time()
    print(f'join global {end-start}')

    start = time.time()
    df_us = df_us_keys.join(df_us, on='key')
    end = time.time()
    print(f'join us {end-start}')

    start = time.time()
    df = pd.concat([dfg,df_us])
    end = time.time()
    print(f'concat {end-start}')

    start = time.time()
    df.set_index(['ISO_A3','state','country_name','date'], inplace=True)
    df.to_pickle(config['FILES']['world_data_frame_pickle'])
    end = time.time()
    print(f'making pickle {end-start}')

    start = time.time()
    df2 = df.copy()
    df2.reset_index(inplace=True)
    end = time.time()
    print(f'copying df {end-start}')

    #Save record of whether a country has states in the data
    start = time.time()
    # df2 = df2[['ISO_A3', 'state']]
    with open(config['FILES']['country_codes'], 'wt') as f:
        for country_code in df2['ISO_A3'].unique():
            if country_code in states_of_country.keys():
                has = '1'
            else:
                has = '0'
            f.write(country_code + ',' + has+'\n')
    end = time.time()
    print(f'saving what countries have states {end-start}')

    start = time.time()

    #Save record of the states in a country
    with open(config['FILES']['states_of_country'], 'wt') as f:
        for country_code in df2['ISO_A3'].unique():
            if country_code in states_of_country.keys():
                for state in states_of_country[country_code]:
                    f.write(country_code + ',' + state + '\n')
    end = time.time()
    print(f'everything else {end-start}')
    return None, df

if __name__ == '__main__':
    import doctest
    status, df = make_pickle()
    print(f'pickle made - end date: {df.index.get_level_values("date").max()}')
    #doctest.testmod(verbose=False)
