# Removed from make_world_features.py
def get_nation_time_series(df1, ISO_A3, start_date, end_date):

    # Get population
    config = get_config()
    pop=-1
    path = config['FILES']['world_census']
    with open(path,"r") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[1] == ISO_A3:
                pop = int(row[2])
                break;
    if pop <= 0:
        return None, None

    # Select county and date range
    df1 = df1[df1.date >= start_date]
    df1 = df1[df1.date <= end_date][['date','deaths']]
    df1 = df1.groupby('date').deaths.sum().reset_index()
    df1.deaths *= 100000/pop
    jsonstr = df1.to_json(orient='records')

    config = get_config()

    start_date = format(start_date,"%x")
    end_date = format(end_date,"%x")
    jsonstr = '{' + f'"start_date": "{start_date}", "end_date": "{end_date}", "stats":' + jsonstr + '}'

    return None, jsonstr
