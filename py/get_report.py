import csv
from get_config import get_config

config = get_config()

path = config['FILES']['us_covid_deaths']
start_date ='9/14/20'
end_date = '10/14/20'
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
            ndeaths = int(row[col_last_date]) - int(row[col_first_date])
            print(f'Cook county {ndeaths} deaths from {start_date} to {end_date}')
            pop = 5150233
            print(f'Cook county per capita {100000*ndeaths/pop}')
            last_cook_deaths += int(row[col_last_date])
        if row[6] == 'Illinois':
            illinois_deaths += int(row[col_last_date])-int(row[col_first_date])
    print(f'Illinois {illinois_deaths} deaths from start date to end date')
    pop = 12671821
    cook_pop = 5150233
    print(f'Illinois per capita {100000*illinois_deaths/pop}')
    print(f'Cook last deaths {last_cook_deaths}')
    print(f'Cook last per capita {100000*last_cook_deaths/cook_pop}')

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
            ndeaths = int(row[col_last_date]) - int(row[col_first_date])
            print(f'Ontario {ndeaths}')
            pop = 12851821
            print(f'Ontario per capita {100000*ndeaths/pop}')