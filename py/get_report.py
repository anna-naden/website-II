import csv
from get_config import get_config

config = get_config()

path = config['FILES']['us_covid_deaths']
start_date ='9/15/20'
end_date = '10/15/20'
illinois_pop = 12671821
cook_pop = 5150233
ontario_pop = 12851821

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
            last_cook_deaths += int(row[col_last_date])
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
                elif  row[i] == start_date:
                    col_first_date = i
            header=False
        if row[0] == 'Ontario':
            ndeaths_ontario = int(row[col_last_date]) - int(row[col_first_date])

print('ILLINOIS')
print(f'{illinois_deaths} deaths from start date to end date')
print(f'per capita {100000*illinois_deaths/illinois_pop}')
print('\n')

print('COOK')
print(f'Last deaths {last_cook_deaths}')
print(f'Last per capita {100000*last_cook_deaths/cook_pop}')
print(f'{ndeaths_cook} deaths from {start_date} to {end_date}')
print(f'Per capita {100000*ndeaths_cook/cook_pop}')

print('ONTARIO')
print(f'Deaths {ndeaths_ontario}')
print(f'Per capita {100000*ndeaths_ontario/ontario_pop}')
