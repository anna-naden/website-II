from get_config import get_config
from get_world_census import get_country_code
from read_parse_aliases import read_parse_aliases
import datetime
import numpy as np
import csv
import pandas as pd

def transpose(lines):
    config = get_config()
    alias_dict = read_parse_aliases(config['FILES']['country_aliases'])
    

    header = lines[0]
    length = len(header)
    i=1
    for line in lines[1:]:
        if len(line) != length:
            return f'world covid file format len(header): {length} i: {i} len(line): {len(line)}', None
        i += 1
    dates = np.empty(shape=length-4, dtype=datetime.datetime)
    for i in range(length-4):
        datestr = header[i+4]
        dateobj = datetime.datetime.strptime(datestr,'%m/%d/%y')
        dates[i]= dateobj
    ndates = length-4
    nrecords = len(lines)-1
    countries = np.empty(shape=nrecords*ndates, dtype=(str,3))
    country_names = np.empty(shape=nrecords*ndates, dtype=(str,48))
    dates2 = np.empty(shape=nrecords*ndates, dtype=datetime.datetime)
    deaths_or_cases = np.empty(shape=nrecords*ndates, dtype=np.int32)
    states = np.empty(shape=nrecords*ndates, dtype=(str,48))
    i=0
    for irecord in range(nrecords):
        line = lines[irecord+1]
        state = line[0]
        alias = line[1]
        if alias in alias_dict.keys():
            country_name = alias_dict[alias]
        else:
            country_name = alias
        country_code = get_country_code(country_name)
        if country_code != 'XXX' and country_code != 'USA':    #Did country code lookup succeed?
            for idate in range(ndates):
                states[i] = state
                country_names[i]=country_name
                countries[i]=country_code
                dates2[i]= dates[idate]
                deaths_or_cases[i]=line[idate+4]
                i += 1

    #We skipped over some countries because we couldn't find a country code
    nrecords = i-1
    states = states[:nrecords]
    countries = countries[:nrecords]
    country_names=country_names[:nrecords]
    dates2 = dates2[:nrecords]
    deaths_or_cases = deaths_or_cases[:nrecords]

    return None, ndates, nrecords, states, countries, country_names, dates2, deaths_or_cases

def transpose_us(lines, index_first_date):

    header = lines[0]
    length = len(header)
    for line in lines[1:]:
        if len(line) != length:
            return 'us covid file format', None

    dates = np.empty(shape=length-index_first_date, dtype=datetime.datetime)
    for i in range(length-index_first_date):
        datestr = header[i+index_first_date]
        dateobj = datetime.datetime.strptime(datestr,'%m/%d/%y')
        dates[i]= dateobj
    ndates = length-index_first_date
    nrecords = len(lines)-1
    counties = np.empty(shape=nrecords*ndates, dtype=(str,48))
    states = np.empty(shape=nrecords*ndates, dtype=(str,48))
    fips_list = np.empty(shape=nrecords*ndates, dtype=(str,5))
    dates2 = np.empty(shape=nrecords*ndates, dtype=datetime.datetime)
    deaths_or_cases = np.empty(shape=nrecords*ndates, dtype=np.single)
    combined_keys = np.empty(shape=nrecords*ndates, dtype=(str,64))

    i=0
    for irecord in range(nrecords):
        line = lines[irecord+1]
        fips = line[4]
        if fips != '':
            fips = '{:05d}'.format(int(float(line[4])))
            county=line[5]
            state = line[6]
            combined_key = line[10]

            for idate in range(ndates):
                states[i]=state
                combined_keys[i]=combined_key
                counties[i]=county
                fips_list[i]=fips
                dates2[i]= dates[idate]
                try:
                    deaths_or_cases[i]=line[idate + index_first_date]
                except Exception as ex:
                    print(ex)
                    exit()
                i += 1
    i -= 1
    states = states[:i]
    combined_keys = combined_keys[:i]
    counties = counties[:i]
    fips_list = fips_list[:i]
    counties = counties[:i]
    dates2 = dates2[:i]
    deaths_or_cases = deaths_or_cases[:i]

    return None, ndates, nrecords, fips_list, counties, states, combined_keys, dates2, deaths_or_cases

def build_df(cases_lines, death_lines, us_cases_lines, us_death_lines, keep_index):

    list1 = transpose(death_lines)
    status = list1[0]
    if status is not None:
        return status, None
    status, ndates, nrecords, states, countries, country_names, dates, deaths = list1
    
    list1 = transpose(cases_lines)
    status = list1[0]
    if status is not None:
        return status, None
    status, ndates2, nrecords2, states2, countries2, country_names2, dates2, cases = list1

    #Verify that the deaths data has one-to-one correspondence with the cases data
    try:
        assert (ndates==ndates2)
        assert (nrecords == nrecords2)
        assert (states == states2).all
        assert (countries == countries2).all
        assert (country_names == country_names2).all
        assert (dates == dates2).all
    except Exception as inst:
        return f'Comparing international cases with international deatths{inst}', None

    index_first_date = 12
    list1 = transpose_us(us_death_lines, index_first_date)
    status = list1[0]
    if status is not None:
        return status, None
    status, ndates_us, nrecords_us, fips, counties, states_us, combined_keys, dates_us, deaths_us = list1

    index_first_date = 11
    list1 = transpose_us(us_cases_lines, index_first_date)
    status = list1[0]
    if status is not None:
        return status, None
    status, ndates_us2, nrecords_us2, fips2, counties2, states_us2, combined_keys2, dates_us2, cases_us = list1

    #Verify that the deaths data has one-to-one correspondence with the cases data
    try:
        assert (ndates_us==ndates_us2)
        assert (nrecords_us == nrecords_us2)
        assert (fips == fips2).all
        assert (counties == counties2).all
        assert (states_us == states_us2).all
        assert (dates_us == dates_us2).all
    except Exception as inst:
        return f'Comparing us deaths with us cases: {inst}', None

    #Verify that the us data has one-to-one correspondence with the international data
    try:
        assert (ndates==ndates_us)
    except Exception as inst:
        return f'comparing us data with international data {inst}', None

    #Non-us data
    fips_dummy = np.empty(shape=len(states), dtype=(str,3))
    fips_non_us = fips_dummy
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
    for i1 in range(len(countries)):
        if countries[i1] == 'CAN':
            fips_non_us[i1] = canada_fips[states[i1]]
    counties_dummy=np.empty(shape=len(states), dtype=(str,48))
    combined_keys_dummy = np.empty(shape=len(states), dtype=(str,64))
    data = {'fips': fips_dummy, 'state_fips': fips_non_us,'county': counties_dummy, 'combined_keys': combined_keys_dummy, 'state': states, \
        'country_name': country_names, 'date': dates, 'ISO_A3': countries, 'cases': cases, 'deaths': deaths}
    #print(len(states),len(country_names), len(dates), len(countries), len(deaths), len(cases))
    df = pd.DataFrame(data=data)

    #US data
    us_names = np.full(shape=len(states_us), dtype=(str,48), fill_value='USA')
    us_codes = us_names

    state_fips = fips.copy()
    ifip=0
    for fip in state_fips:
        state_fips[ifip] = state_fips[ifip][0:2]
        ifip += 1
    
    data = {'fips': fips, 'state_fips': state_fips, 'county': counties, 'combined_keys': combined_keys, 'state': states_us, \
        'country_name': us_names, 'date': dates_us, 'ISO_A3': us_codes, 'cases': cases_us, 'deaths': deaths_us}
    df_us = pd.DataFrame(data=data)
    df2 = pd.concat([df,df_us])
    
    #Handle countries whose data is not broken down by state or province
    df2=df2.replace('',np.nan)
    if keep_index:
        df2 = df2.set_index(['state', 'country_name', 'fips','date', 'ISO_A3', 'county'])

    #Write csv file for testing purposes
    #df2.to_csv('jh_df.csv')

    return None, df2

#    To validate the structure and content of the four arrays, write a csv file

    # with open('temp_cases.csv','w') as f:
    #     writer = csv.writer(f)
    #     for i in range(nrecords*ndates):
    #         writer.writerow([states[i],countries[i],country_names[i], dates[i],cases[i]])

    # with open('temp_deaths.csv','w') as f:
    #     writer = csv.writer(f)
    #     for i in range(nrecords2*ndates2):
    #         writer.writerow([states2[i],countries2[i],country_names[i], dates2[i],deaths[i]])

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
    try:
        with open(config['FILES']['world_covid_deaths'], 'rt', newline='') as f:
            reader = csv.reader(f)
            death_lines = []
            for row in reader:
                death_lines.append(row)
        with open(config['FILES']['world_covid_cases'], 'rt', newline='') as f:
            reader = csv.reader(f)
            cases_lines = []
            header = True
            length=0
            for row in reader:
                cases_lines.append(row)
                if header:
                    length = len(row)
                else:
                    row = row[:length]
                header = False
        with open(config['FILES']['us_covid_deaths'], 'rt', newline='') as f:
            reader = csv.reader(f)
            us_death_lines = []
            for row in reader:
                us_death_lines.append(row)
        with open(config['FILES']['us_covid_cases'], 'rt', newline='') as f: 
            reader = csv.reader(f)
            us_cases_lines = []
            for row in reader:
                us_cases_lines.append(row)
    except Exception as inst:
        return inst, None
        
    status, df = build_df(cases_lines, death_lines, us_cases_lines, us_death_lines, keep_index)
    df.to_pickle(config['FILES']['world_data_frame_pickle'])
    df2 = df.copy()
    df2.reset_index(inplace=True)

    #Save record of whether a country has states in the data
    with open(config['FILES']['country_codes'], 'wt') as f:
        for country_code in df2['ISO_A3'].unique():
            df3 = df2[df2['ISO_A3']==country_code]
            has = '0'
            if not df3['state'].isna().any():
                has = '1'
            else:
                has = '0'
            f.write(country_code + ',' + has+'\n')

    #Save record of the states in a country
    with open(config['FILES']['states_of_country'], 'wt') as f:
        for country_code in df2['ISO_A3'].unique():
            df3 = df2[df2['ISO_A3']==country_code]
            if not df3['state'].isna().any():
                for state in df3['state'].unique():
                    f.write(country_code + ',' + state + '\n')

    return status, df

if __name__ == '__main__':
    from df_utils import *
    import doctest

    status, df=make_pickle()
    print(f'pickle made - end data {df.index.get_level_values("date").max()}')
    #doctest.testmod(verbose=False)
