def make_dict_county_graph(df1, pop, fips, start_date, end_date):
    """ Make dictionary for Javascript object to drive county d3 graph

    Args:
        df1 (DataFrame): dates and deaths for county
        pop (int): population of county
        fips (str): identifier for county
        start_date (Pandas timestamp) the start of the interval over which deaths are summed
        end_date

    Returns:
        [dictionary) corresponds to Javascript object that d3 will use to make graph
    """

    df = df1.copy()[['date','deaths']]
    df.deaths *= 100000/pop

    jsonstr = df.to_json(orient='records')
    stats = json.loads(jsonstr)
    config = get_config()
    path = config['FILES']['counties_states']

    try:
        df = pd.read_csv(path, dtype={'FIPS':str, 'county':str, 'state_abbr':str, 'state': str})
    except Exception as inst:
        return f'Exception reading {path} {inst})', None
    df = df[df.FIPS==fips]
    if not df.empty:
        start_date = format(start_date,"%x")
        end_date = format(end_date,"%x")
        county_state = df.iloc[0].county + ' County, ' + df.iloc[0].state_abbr
        dict_cty_graph = {"start_date": start_date, "end_date": end_date, "county": county_state, "stats": stats}

        return None, dict_cty_graph
    return None, None

# County time series
df_time_series = df[['fips','date','deaths']]
df_time_series = df_time_series[df_time_series.date>=start_date_graph]
df_time_series = df_time_series[df_time_series.date<=end_date]
all_json = '{'
first=True
all_counties = {}
for county_fips in df.fips.unique():
    # print(county_fips)
    df_county_p = df_pops[df_pops.fips == county_fips]
    df_county = df_time_series[df_time_series.fips == county_fips]
    if not df_county.empty and not df_county_p.empty:
        # delete_obj('covid.phoenix-technical-services.com', county_fips + '.json')
        pop = df_county_p.population.iloc[0]
        status, county_time_series = make_dict_county_graph(df_county, pop, county_fips, start_date_graph, end_date)
        if status is not None:
            print(f'{status} from get_cty_time_series')
            exit(1 )
        if county_time_series is not None:
            all_counties.__setitem__(county_fips, county_time_series)
            # with open('temp.json', 'w') as f:
            #     json.dump(county_time_series, f)
print("Dumping all counties time series to file")
with open(config['FILES']['scratch'], 'w') as f:
    json.dump(all_counties, f)
upload_file(config['FILES']['scratch'], 'covid.phoenix-technical-services.com', 'all_counties.json')
os.remove(config['FILES']['scratch'])

