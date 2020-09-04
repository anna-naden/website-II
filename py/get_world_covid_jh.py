from get_config import get_config
import pandas as pd

def get_world_covid_jh():
    """ Get main dataframe for the application - all the covid data for the whole world
    Args:

    Returns:
        status: None -> success
        df: Dataframe 
    
    >>> status, df = get_world_covid_jh()
    >>> status
    >>> df.empty
    False
    """
    config = get_config()
    try:
        df = pd.read_pickle(config['FILES']['world_data_frame_pickle'])
    except Exception as inst:
        return inst, None
    return None, df

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
