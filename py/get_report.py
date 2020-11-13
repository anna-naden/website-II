import csv
from get_config import get_config

config = get_config()

start_date ='10/8/20'
end_date = '11/8/20'
illinois_pop = 12671821
cook_pop = 5150233
ontario_pop = 12851821
france_pop = 66977107
us_pop = 326687501
mex_pop = 126190788

path = config['FILES']['us_covid_deaths']
with open(path, 'r') as f:
    reader = csv.reader(f, delimiter=',')
    header = True
    illinois_deaths = 0
    last_cook_deaths = 0
    for row in reader:
        if header:
            for i in range(len(row)):
                if row[i] == end_date:
                    col_last_date = i
                elif row[i] == start_date:
                    col_first_date = i
            header=False
        if  row[4] == '17031.0':
            ndeaths_cook = int(row[col_last_date]) - int(row[col_first_date])
            last_cook_deaths = int(row[col_last_date])
        if row[6] == 'Illinois':
            illinois_deaths += int(row[col_last_date])-int(row[col_first_date])

with open(config['FILES']['world_covid_deaths'], 'r') as f:
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
            header=False
        if row[0] == 'Ontario':
            ndeaths_ontario = int(row[col_last_date]) - int(row[col_first_date])
        elif row[0] == '' and row[1] == 'France':
            last_ndeaths_france = int(row[col_last_date])
            last_wk_fr_deaths = int(row[col_last_week])
        elif row[1] == 'US':
            last_ndeaths_us = int(row[col_last_date])
        elif row[1] == 'Mexico':
            last_ndeaths_mex = int(row[col_last_date])

print('US')
print(f'Last deaths: {last_ndeaths_us}')
print(f'per capita {100000*last_ndeaths_us/us_pop}')
print('\n')

print('FRA')
print(f'Last deaths {last_wk_fr_deaths}, {last_ndeaths_france}')
print(f'Last week d per cap: {100000*(last_ndeaths_france-last_wk_fr_deaths)/(7*france_pop)}')
print(f'per capita {100000*last_ndeaths_france/france_pop}')
print('\n')

print('MEX')
print(f'Last deaths {last_ndeaths_mex}')
print(f'per capita {100000*last_ndeaths_mex/mex_pop}')
print('\n')

print('ONTARIO')
print(f'Deaths {ndeaths_ontario}')
print(f'Per capita {100000*ndeaths_ontario/ontario_pop}')
print('\n')

print('ILLINOIS')
print(f'{illinois_deaths} deaths from start date to end date')
print(f'per capita {100000*illinois_deaths/illinois_pop}')
print('\n')

print('COOK')
print(f'Last deaths {last_cook_deaths}')
print(f'Last per capita {100000*last_cook_deaths/cook_pop}')
print(f'{ndeaths_cook} deaths from {start_date} to {end_date}')
print(f'Per capita {100000*ndeaths_cook/cook_pop}')

