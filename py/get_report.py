import csv
from get_config import get_config

config = get_config()

path = config['FILES']['us_covid_deaths']
start_date ='8/23/20'
end_date = '9/22/20'
with open(path, 'r') as f:
    reader = csv.reader(f, delimiter=',')
    header = True
    illinois_deaths = 0
    for row in reader:
        if header:
            print(row[20])
            for i in range(len(row)):
                if row[i] == end_date:
                    col_last_date = i
                elif row[i] == start_date:
                    col_first_date = i
            header=False
        if  row[4] == '17031.0':
            print(row[col_first_date])
            print(row[col_last_date])
            ndeaths = int(row[col_last_date]) - int(row[col_first_date])
            print(f'Cook county {ndeaths} deaths from {start_date} to {end_date}')
            print(f'Cook county per capita {100000*ndeaths/5150233}')
        if row[6] == 'Illinois':
            illinois_deaths += int(row[col_last_date])-int(row[col_first_date])
    print(f'Illinois {illinois_deaths} deaths from start date to end date')
    print(f'Illinois per capita {100000*illinois_deaths/12671821}')