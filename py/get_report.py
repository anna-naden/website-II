import csv
from get_config import get_config

def map_us(path, end_date):
    cook = '17031.0'
    gregory = '46053.0'
    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        header = True
        illinois_deaths = 0
        last_cook_deaths = 0
        illinois_deaths_wk = 0
        for row in reader:
            if header:
                for i in range(len(row)):
                    if row[i] == end_date:
                        col_last_date = i
                        col_first_date = i-7
                    if row[i] == week_end:
                        col_week_end_us = i
                header=False
            if  row[4] == cook:
                ndeaths_cook = int(row[col_last_date]) - int(row[col_first_date])
                last_cook_deaths = int(row[col_last_date])
                ndeaths_cook_week = int(row[col_week_end_us]) - int(row[col_week_end_us-7])
            if row[4] == gregory:
                ndeaths_gregory_week = int(row[col_week_end_us]) - int(row[col_week_end_us-7])
            if row[6] == 'Illinois':
                illinois_deaths += int(row[col_last_date])-int(row[col_first_date])
                illinois_deaths_wk += int(row[col_week_end_us]) - int(row[col_week_end_us-7])
    f.close()
    return col_first_date, col_last_date, ndeaths_cook, last_cook_deaths, ndeaths_cook_week, ndeaths_gregory_week, illinois_deaths, illinois_deaths_wk

def map_world(path, start_date, end_date, week_start, week_end, doctest_date):
    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        header = True
        for row in reader:
            if header:
                for i in range(len(row)):
                    if row[i] == end_date:
                        col_last_date = i
                        col_last_week = i-7
                    elif  row[i] == start_date:
                        col_first_date = i
                    if row[i] == week_start:
                        col_week_start = i
                    elif row[i] == week_end:
                        col_week_end = i
                    if row[i] == doctest_date:
                        col_doctest_global = i
                header=False
            if row[0] == 'Ontario':
                ndeaths_ontario = int(row[col_last_date]) - int(row[col_first_date])
                week_ndeaths_ontario = int(row[col_week_end]) - int(row[col_week_start])
            elif row[0] == '' and row[1] == 'France':
                last_ndeaths_france = int(row[col_last_date])
                wk_fr_deaths = int(row[col_week_end]) - int(row[col_week_start])
            elif row[1] == 'US':
                last_ndeaths_us = int(row[col_last_date])
                wk_us_deaths = int(row[col_week_end]) - int(row[col_week_start])
                doctest_us_ndeaths = int(row[col_doctest_global])
            elif row[1] == 'Mexico':
                last_ndeaths_mex = int(row[col_last_date])
                week_mx_deaths = int(row[col_week_end]) - int(row[col_week_start])
                doctest_mx_ndeaths = int(row[col_doctest_global])
            elif row[1] == 'Bulgaria':
                last_ndeaths_bulg = int(row[col_last_date])
                week_bulg_ndeaths = int(row[col_week_end]) - int(row[col_week_start])
    f.close()
    return col_last_date, col_last_week, col_first_date, col_doctest_global, week_ndeaths_ontario, wk_fr_deaths, wk_us_deaths, doctest_mx_ndeaths, doctest_us_ndeaths, \
        ndeaths_ontario, last_ndeaths_france, last_ndeaths_us, last_ndeaths_mex, week_mx_deaths, last_ndeaths_bulg, week_bulg_ndeaths
    

config = get_config()

start_date_for_world ='11/13/20'
end_date = '12/26/20'
week_start = '12/19/20'
week_end = '12/26/20'
doctest_date ='4/10/20' #for testing make_pickle
print(f'start date for world {start_date_for_world} end date for us/world {end_date} week start for world {week_start} week end for world {week_end} doctest date {doctest_date}')

col_first_date, col_last_date, ndeaths_cook, last_cook_deaths, ndeaths_cook_week, ndeaths_gregory_week, illinois_deaths, illinois_deaths_wk = \
    map_us(config['FILES']['us_covid_deaths'], end_date)

col_last_date, col_last_week, col_first_date, col_doctest_global, week_ndeaths_ontario, wk_fr_deaths, wk_us_deaths, doctest_mx_ndeaths, doctest_us_ndeaths, \
        ndeaths_ontario, last_ndeaths_france, last_ndeaths_us, last_ndeaths_mex, week_mx_deaths, last_ndeaths_bulg, week_bulg_ndeaths = \
        map_world(config['FILES']['world_covid_deaths'], start_date_for_world, end_date, week_start, week_end, doctest_date)

illinois_pop = 12671821
cook_pop = 5150233
ontario_pop = 14733119
france_pop = 66977107
us_pop = 326687501
mex_pop = 126190788
gregory_pop = 4185
bulg_pop = 7025037

print('US')
print(f'Deaths to date: {last_ndeaths_us}')
print(f'Deaths to date per cap {100000*last_ndeaths_us/us_pop}')
print(f'per capita per day {100000*wk_us_deaths/(7*us_pop)}')
print(f'doctest deaths {doctest_us_ndeaths}')
print('\n')

print('FRA')
print(f'Last week d per cap: {100000*wk_fr_deaths/(7*france_pop)}')
print(f'per capita to date {100000*last_ndeaths_france/france_pop}')
print('\n')

print('MEX')
print(f'Last deaths {last_ndeaths_mex}')
print(f'per capita to date {100000*last_ndeaths_mex/mex_pop}')
print(f'Week deaths per cap {100000*week_mx_deaths/(7*mex_pop)}')
print(f'doctest deaths {doctest_mx_ndeaths}')
print('\n')

print('BULG')
print(f'Last deaths {last_ndeaths_bulg}')
print(f'per capita to date {100000*last_ndeaths_bulg/bulg_pop}')
print(f'Week deaths per cap {100000*week_bulg_ndeaths/(7*bulg_pop)}')
print('\n')

print('ONTARIO')
print(f'Deaths {ndeaths_ontario}')
print(f'Per capita to date {100000*ndeaths_ontario/ontario_pop}')
print(f'week per cap {100000*week_ndeaths_ontario/(7*ontario_pop)}')
print('\n')

print('ILLINOIS')
print(f'{illinois_deaths} deaths from start date to end date')
print(f'per capita to date {100000*illinois_deaths/(7*illinois_pop)}')
print(f'week per cap {100000*illinois_deaths_wk/(7*illinois_pop)}')
print('\n')

print('COOK')
print(f'Last deaths {last_cook_deaths}')
print(f'Last per capita {100000*last_cook_deaths/cook_pop}')
print(f'{ndeaths_cook} deaths from 30 days prior to {end_date}')
print(f'Per capita to date {100000*ndeaths_cook/cook_pop}')
print(f'7-day avg per cap {100000*ndeaths_cook_week/(7*cook_pop)}')
print('\n')

print('GREGORY, SD')
print(f'Week per cap {100000*ndeaths_gregory_week/(7*gregory_pop)}')