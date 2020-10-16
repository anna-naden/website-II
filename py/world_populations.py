import pandas as pd

from get_config import get_config

def world_populations():
    """
    Get a dictionary of world populations keyed by nation code
    Returns: Keys are nation codes. Values are individual dictionaries of 'populatin' --> integer population

    >>> status, df = world_populations()
    >>> status
    >>> df['EGY']['population']
    98423595
    """

    config = get_config()
    path = config['FILES']['world_census']
    try:
        df = pd.read_csv(path, usecols=('Country Name', 'Country Code', 'population'), index_col='Country Code', \
            header=0, dtype={'Country Name': str, 'Country Code': str, 'population': int})
    except Exception as inst:
        return inst, None
    df.rename(columns={'Country Name': 'country_name'}, inplace=True)
    df.index.name='country_code'
    df.drop(inplace=True,axis='columns',labels='country_name')
    return None, df.to_dict(orient='index')

