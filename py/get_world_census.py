import pandas as pd
from get_config import get_config

def get_world_census():
    """ 
    Enumerate countries and of the world based on census with their populations

    Returns:
        DataFrame: Index is country code (nation code). Columns are common name of country, population, common name of region 
    >>> status, df = get_world_census()
    >>> status
    >>> get_countries_of_region('Northern Europe')
    [['Denmark', 'DNK'], ['Estonia', 'EST'], ['Finland', 'FIN'], ['Iceland', 'ISL'], ['Ireland', 'IRL'], ['Latvia', 'LVA'], ['Lithuania', 'LTU'], ['Norway', 'NOR'], ['Sweden', 'SWE'], ['United Kingdom', 'GBR']]
    """
    
    config = get_config()
    path = config['FILES']['world_census']
    try:
        df = pd.read_csv(path, usecols=('Country Name', 'Country Code', 'population', 'region'), index_col='Country Code', \
            header=0, dtype={'Country Name': str, 'Country Code': str, 'population': int, 'region': str})
    except Exception as inst:
        return inst, None

    df.rename(columns={'Country Name': 'country_name'}, inplace=True)
    df.index.name='country_code'
    return None, df

def get_country_code(country_name):
    """
    Look up official three-character country code based on common name of country

    Args:
        country_name (str): Common name of country

    Returns:
        str: Country code
    >>> get_country_code('Mexico')
    'MEX'
    """

    status, df = get_world_census()
    if status is not None:
        return FileNotFoundError
    if df[df.country_name == country_name].empty:
        return 'XXX'
    return df[df.country_name==country_name].index[0]

def get_country_name(country_code):
    """
    Get common name of country

    Args:
        country_code (str): Country code

    Returns:
        str: Common name
    >>> get_country_name('MEX')
    'Mexico'
    """

    status, df = get_world_census()
    if status is not None:
        return FileNotFoundError
    return df.loc[country_code].values[0]

def get_regions():
    """
    Get regions of the world

    Returns:
        List(str): Common names of regions
    >>> x=get_regions()
    >>> x[0]
    'Africa'
    """

    status, df = get_world_census()
    if status is not None:
        return FileNotFoundError
    regions = df.region.to_list()
    myset = set(regions)
    regions = list(myset)
    regions.sort()
    return regions

def get_countries_of_region(region):
    """
    Enumerate countries of a world region

    Args:
        region (str): common name of world region

    Returns:
        List(str,str): Name/code pairs for countries of a region
    >>> mylist=get_countries_of_region('Africa')
    >>> mylist[0]
    ['Algeria', 'DZA']
    """

    status, df = get_world_census()
    if status is not None:
        return FileNotFoundError
    x = df[df.region == region]
    y=x.copy()
    y['country_code']=x.index
    y=y[['country_name','country_code']].to_numpy().tolist()
    y.sort()
    return y

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)
