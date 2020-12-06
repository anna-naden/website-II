"""
    Read the four spreadsheets that are provided by Johns Hoplins University and join and concatenate them to create a pickled data frame. This stand-alone program runs nightly.
"""
import datetime
import csv
import pandas as pd
import time
import numpy as np

from get_config import get_config
from read_parse_aliases import read_parse_aliases
from csv_util import csv_get_dict
from df_utils import *

def save_keys_to_dataframes(keys_global, keys_us):
    """Save the "keys" (the first parts of each row in the spreadsheets) to a data frame so it can later be joined to the "values" 
    (the second parts of each row). A fips column is added to the non-us frame to hold the Canadian version
    of the fips state identifier.

    This function inserts the three-character ISO A3 country codes based on the country names.

    The keys saved here will determine what goes into the final data frame

    Args:
        keys_global: a list, one item for each non-us country or country/state. Each item id a list of the contents of the cells 
        of the "key" part of the row
        keys_us ([type]): Like keys_global, except there is one list item fot each county

    Returns:
        data frame with one row for each non-us country
        data frame with one row for each us county
        dictionary of states for eack country that has individual states. The keys are the three-character ISO-A3 
            country codes
    """
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
            
            ISO_A3 = country_name_dict[country_name]

            if state != '':
                if ISO_A3 not in states_of_country.keys():
                    states_of_country[ISO_A3] = [state]
                else:
                    states_of_country[ISO_A3].append(state)

            # If we don't exclude us here, all the national us cases and deaths will be counted twice.
            if ISO_A3 != 'USA':
                states.append(state)
                country_names.append(key[1])
                lats.append(key[2])
                lons.append(key[3])
                ISO_A3s.append(ISO_A3)

                if country_name == 'Canada' and key[0] in canada_fips.keys():
                    # "Repatriated Travellers"
                    state_fips_s.append(f'{canada_fips[key[0]]}')
                else:
                    state_fips_s.append('')
                keys_global2.append(tuple(key[:2]))
    keys_global = keys_global2

    df_global_keys = pd.DataFrame({'key': keys_global, 'ISO_A3': ISO_A3s, 'state': states, \
        'state_fips': state_fips_s, 'country_name': country_names, 'lat': lats, 'lon': lons}).set_index('key')

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
        populations.append(int(key[11]))
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

    df_us_keys = pd.DataFrame(\
        {'key' : keys, \
        'fips': fips_s, \
        'state_fips': state_fips_s, \
        'country_name': country_names, \
        'ISO_A3': ISO_A3s, 
        'county': counties, \
        'UID': UIDs, \
        'isos2': iso2s, \
        'isos3': iso3s, \
        'code3': code3s, \
        'FIPs': FIPs, \
        'Admin2': Admin2s, \
        'state': states, \
        'country_region': country_regions, \
        'latitude': lats, \
        'longitude': lons, \
        'combined_key': combined_keys, \
        'population': populations})\
        .set_index('key')
    return df_global_keys, df_us_keys, states_of_country

def read_csvs():
    """Read the four spreadsheets that are downloaded nightly from the Johns Hopkind website 
    and check that the cases data is consistent with the deaths data

    Returns:
        For each spreadsheet, a list of lists of strings. Each list of strings represents one
        row. The header rows are included
    """
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

def parse_spreadsheet(date_start_global, dd_us, dc_us, death_lines, cases_lines, us_death_lines, us_cases_lines):
    """Parse the non-header rows of the four spreadsheets and compare the "cases" keys with the "deaths" keys

    Args:
        date_start_global int: The column number in the header row where the dates start for non-us. For other rows, this
            is where the deaths or cases start
        dd_us int: column number where deaths start for us
        dc_us: int: column number where cases start

        death_lines list of lists of strings, one list of strings for each row in the spreadsheet after the header
        cases_lines: similar
        us_death_lines: similar
        us_cases_lines: similar

    Returns:
        keys_global: List of lists of strings. The "key" portion of the each row from the csv file, stripped of the variable floating
            point part so that only the state (if any) and country part remain.
        keys_us: list of lists similar to keys_global but representing more than just state/country but also fips code, county, ect.

        Because the keys for deaths are identical to the keys for cases, only one of the two is returned.

        values_global_d: list of lists of strings. The cumulative deaths for each day for non-us countries
        values_global_c similar to values_global_d but cases insted of deaths.
        values_us_d, values_us_c: similar to above, but for us
    """
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

def make_pickle():
    """
    Read the four spreadsheets that are provided by Johns Hoplins Universit,y, compare them, fill in identifiers
     and combine them to create a pickled, non-normalized data frame. This stand-alone program runs nightly.

    Args:
        None

    Returns:
        status: None if successful
        DataFrame: Indexed by ISO-A3 nation code, common names of country/state/county, fipd id 
            and date. Columns are cases and fatalities, population, latitude and longitude
    
    >>> status, df = make_pickle()
    >>> status
    >>> df = df[df.index.get_level_values('ISO_A3')=='MEX']
    >>> df = df[df.index.get_level_values('date') == '2020-04-10']
    >>> get_value_by_col(df, 'cases')   #mx
    3844
    >>> get_value_by_col(df, 'deaths') #mx
    233
    >>> status, df = make_pickle()
    >>> status
    >>> df = df[df.index.get_level_values('ISO_A3')=='USA']
    >>> get_value_by_date_col(df, '2020-04-10', 'cases') #us
    503474.0
    >>> get_value_by_date_col(df, '2020-04-10', 'deaths') #us
    23403.0
    """
    config = get_config()
    
    # Read the downloaded Johns Hopkins spreadsheets
    death_lines, cases_lines, us_death_lines,us_cases_lines = read_csvs()

    ##################################################################################
    # Map the rows and columns of the spreadsheets
    ##################################################################################

    d_header = death_lines.pop(0)
    d_us_header = us_death_lines.pop(0)
    c_header = cases_lines.pop(0)
    c_us_header = us_cases_lines.pop(0)
    assert (d_header == c_header)
    
    # Where the date info starts
    date_start_global = d_header.index('Long') + 1
    dd_us = d_us_header.index('Population') + 1 #deaths
    dc_us = c_us_header.index('Combined_Key') + 1   #cases
    assert (d_header[date_start_global:]==d_us_header[dd_us:])
    assert (d_us_header[dd_us:]== c_header[date_start_global:])
    assert (c_header[date_start_global:]==c_us_header[dc_us:])
    dates = d_header[date_start_global:]

    #Separate keys from values
    keys_global, keys_us, values_global_d, values_global_c, values_us_d, values_us_c = \
        parse_spreadsheet(date_start_global, dd_us, dc_us, death_lines, cases_lines, us_death_lines, us_cases_lines)

    #Save keys to dataframes
    df_global_keys, df_us_keys, states_of_country = save_keys_to_dataframes(keys_global, keys_us)

    #############################################################################
    # Create data structure for non-US data frame
    ############################################################################
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
    # print(f'making df_global {end-start}')

    #############################################################################
    # Create data structure for US data frame
    ############################################################################

    start = time.time()
    expanded_dates = []
    expanded_keys = []
    cases = []
    deaths = []
    dates2=[]
    deaths = []
    cases = []
    expanded_dates = []
    expanded_keys = []

    #Convert date strings to dateobjects
    for date in dates:
        dates2.append(datetime.datetime.strptime(date,'%m/%d/%y'))

    #Convert cases and deaths, string to integer
    for k in values_us_d.keys():
        values_us_d[k] = map(int, values_us_d[k])
    for k in values_us_c.keys():
        values_us_c[k] = map(int, values_us_c[k])

    #The resulting lists will have one item for each key/date combination
    for key in keys_us:
        tkey = tuple(key[:8])
        idate = 0
        deaths += values_us_d[tkey]
        cases += values_us_c[tkey]
        expanded_dates += dates2
        expanded_keys += len(dates2)*[tkey]
    end = time.time()
    # print(f'creating data structure for df_us {end-start}')

    start = time.time()
    df_us = pd.DataFrame({'key': tuple(expanded_keys), 'date':expanded_dates, 'cases': cases, 'deaths': deaths}).set_index('key')
    end = time.time()
    # print(f'making df_us {end-start}')

    #de-normalize non-us data
    dfg = df_global_keys.join(df_global, on='key')

    #denormalize us data
    start = time.time()
    df_us = df_us_keys.join(df_us, on='key')
    end = time.time()
    # print(f'join us {end-start}')

    #Combine us and non-us data
    start = time.time()
    df = pd.concat([dfg,df_us])
    end = time.time()
    # print(f'concat {end-start}')

    #Put data frame in final form and save
    start = time.time()
    df.set_index(['ISO_A3','state','country_name','date'], inplace=True)
    # df.drop(['lat','lon','UID','Admin2','country_region','latitude','longitude','combined_key'], axis='columns')
    df.to_pickle(config['FILES']['world_data_frame_pickle'])
    end = time.time()
    # print(f'making pickle {end-start}')

    #Save record of whether a country has states in the data
    with open(config['FILES']['country_codes'], 'wt') as f:
        for country_code in df.index.get_level_values('ISO_A3').unique():
            if country_code in states_of_country.keys():
                has = '1'
            else:
                has = '0'
            f.write(country_code + ',' + has+'\n')

    #Save record of the states in a country
    with open(config['FILES']['states_of_country'], 'wt') as f:
        for country_code in df.index.get_level_values('ISO_A3').unique():
            if country_code in states_of_country.keys():
                for state in states_of_country[country_code]:
                    f.write(country_code + ',' + state + '\n')
    return None, df

if __name__ == '__main__':
    import doctest
    start = time.time()
    status, df = make_pickle()
    end = time.time()
    print(f'pickle made - end date: {str(df.index.get_level_values("date").max())[:10]} {round(end-start,2)} seconds')
    # doctest.testmod(verbose=False)