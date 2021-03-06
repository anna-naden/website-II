from csv import reader

def csv_lookup(path, key_col, key, value_col):
    found = False
    try:
        with open(path,'r') as f:
            csv_reader = reader(f)
            for row in csv_reader:
                # row variable is a list that represents a row in csv
                if row[key_col]==key:
                    value = row[value_col]
                    found = True
                    break
        if found:
            return None, value
    except Exception as ex:
        return ex, None

    return "Key Error", None

def csv_get_dict(path, key_col, value_col, header=False):
    dict = {}
    try:
        first = True
        with open(path, 'r') as f:
                csv_reader = reader(f)
                for row in csv_reader:
                    if not header or not first:
                        key = row[key_col]
                        if key in dict:
                            return None
                        dict[key] = row[value_col]
                    first = False
    except Exception as ex:
        return ex, None
    return dict
