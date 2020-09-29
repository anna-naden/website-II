def read_parse_aliases(path):
    """
    Read a file where each line is an alias, followed by '|', followed by a value
    """
    dict = {}
    with open(path,'rt') as f:
        while(True):
            line = f.readline()
            if not line:
                break
            if line[0] != '#':
                line=line.strip('\n')
                alias, value = line.split('|')
                dict[alias] = value
    return dict
