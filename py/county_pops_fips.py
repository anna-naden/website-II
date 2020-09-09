from get_config import get_config
import pandas as pd

def county_pops_fips(nation_code='USA'):
    """ Look up population for all counties in USA by FIPS

    Args:
        nation_code (str, optional): Official nation cod. Defaults to 'USA'.

    Returns:
        DataFrame: Columns are county FIPS, state FIPS, five-character FIPS code, state name, county name and population
    >>> status, df =county_pops_fips()
    >>> status
    >>> df = df[df.county == 'Autauga County']
    >>> df = df[df.state == 'Alabama']
    >>> get_str_one_row(df, 'county_fips')
    '001'
    >>> get_str_one_row(df, 'state_fips')
    '01'
    >>> get_value_by_col_one_row(df, 'population')
    55869
    >>> get_str_one_row(df,'fips')
    '01001'
    """


    if nation_code != 'USA':
        return 'Not implemented', pd.DataFrame()

    config = get_config()
    path = config['FILES']['county_census']
    try:
        dfc = pd.read_csv(path, usecols=['STATE','COUNTY', 'POPESTIMATE2019', 'STNAME', 'CTYNAME'], \
            dtype={'STNAME': str, 'CTYNAME': str, 'STATE': str, 'COUNTY': str, 'POPESTIMATE2019': int}, \
                encoding='latin-1')
    except Exception as inst:
        return inst, pd.DataFrame()
    dfc.rename(axis='columns', mapper={'STATE': 'state_fips', 'COUNTY': 'county_fips', 'POPESTIMATE2019': 'population', \
        'STNAME': 'state', 'CTYNAME':'county'}, inplace=True)
    dfc['fips'] = dfc.state_fips + dfc.county_fips
    return None, dfc