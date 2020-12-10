# Time series all nations
for key in nations.keys():
# for key in ['USA']:
    status, time_series_json = get_nation_time_series(df_world1[df_world1.ISO_A3==key].copy(), key, start_date_graph, end_date)
    if status is not None:
        print(status)
        exit(1)
    if time_series_json is not None:
        with open(config['FILES']['scratch'], 'w') as f:
            f.write(time_series_json)
            # upload_file(config['FILES']['scratch'], 'covid.phoenix-technical-services.com',key+'.json', key)
            delete_obj('covid.phoenix-technical-services.com', key+'.json')
            upload_file(config['FILES']['scratch'], 'covid.phoenix-technical-services.com',key+'.json', key)
            os.remove(config['FILES']['scratch'])
    else:
        print(f'\nskipping {key}')
