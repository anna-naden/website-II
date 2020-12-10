def make_csv_bar_charts(state_deaths):
    config = get_config()

    path = config['FILES']['js']+'/barchart.js'
    with open(path, 'w') as f:
        f.write('var data = [\n')
        state_name_dict = csv_get_dict(config['FILES']['state_fips'], 1, 0)
        for state in state_deaths.keys():
            if state[3:] in state_name_dict.keys():
                state_name = state_name_dict[state[3:]]
                f.write('{\n')
                f.write(f'"name": "{state_name}",\n')
                f.write(f'"value": {state_deaths[state]},\n')
                f.write('},\n')
        f.write('];')
    f.close()

