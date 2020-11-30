import pandas as pd

def get_value_by_date_col(df, date, column):
    """
    Get a numerical value from a data frame

    Args:
        df (DataFrame): The data frame from which to get the value
        date (str or datetime): The date for which to get the data
        column (str): The column from which to get the data

    """

    dfgb = df.groupby('date').sum()
    return dfgb[dfgb.index == date].iloc[0][column]

def get_value_by_col(df, column):
    """
    Get a numerical value or a pair from a data frame

    Args:
        df (DataFrame): The data frame from which to get the value
        column (str): The column from which to get the data
    """

    return get_value_by_col_one_row(df, column)

def get_value_by_col_one_row(df, column):
    """
    Get a numerical value or a pair from a data frame

    Args:
        df (DataFrame): The data frame from which to get the value
        column (str): The column from which to get the data
    """

    if df.empty:
        raise Exception('No data')
    if df.shape[0] != 1:
        raise Exception('Too much data')
    return df.iloc[0][column]

    return df[column]

def get_str_one_row(df, column):
    """
    Get string from data frame with one row

    Args:
        df (DataFrame): The data
        column (str): The column

    >>> status, df = get_states_and_counties('USA')
    >>> df = df[df.state == 'Alabama']
    >>> df = df[df.county == 'Autauga']
    >>> get_str_one_row(df, 'FIPS')
    '01001'
    """

    if df.empty:
        raise Exception('No data')
    if df.shape[0] != 1:
        raise Exception('Too much data')
    df2=df.copy()
    df2.reset_index(inplace=True)
    if column in df2.columns:
        return df2.iloc[0][column]

def get_str_first_row(df, column):
    """
    Get string from data frame with one row

    Args:
        df (DataFrame): The data
        column (str): The column

    """

    if df.empty:
        raise Exception('No data')
    return df.iloc[0][column]

if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=False)

