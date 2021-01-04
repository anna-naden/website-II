import configparser
import os

def get_config():
    """ Get the configuration dictionary (analogous to Windows ini file) for the application

    Returns:
     dictionary: indexed by string group and string key
    >>> config = get_config()
    >>> config['FILES']['test']
    'test'
    """

    config = configparser.ConfigParser()
    # config_path = 'C:\\Users\jean0\\Dropbox\\projects\\website-II\\config.ini'
    config_path = '/home/anna_user2/Dropbox/projects/website-II/config.ini'

    config.read(config_path)
    return config

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)
