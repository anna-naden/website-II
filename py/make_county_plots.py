"""Generate and upload raster images of covid plots, one for each nation. This stand-alone program
runs weekly or nightly

"""
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import datetime

from get_world_covid_jh import get_world_covid_jh
from world_populations import world_populations
from get_config import get_config
from csv_util import csv_get_dict
from send_content import send_content

def get_nation_weekly(df, pop):
    """ Generate lists or arrays of x and y values for a single nation based on daily change averaged over seven days

    Args:
        df Dataframe for a nation
        pop int, population

    Returns:
        Pandas date-time index of weekly dates (array-like)
        Array of average daily deaths per 100,000 people
    """
    ndays=7
    l = len(df)
    deaths = df.deaths
    dates = df.index.get_level_values('date')
    nd =[]
    dates2 =[]
    i1 = (l-1) %ndays
    for i in range(i1,l,ndays):
        di = deaths[i]
        di1 = deaths[i-ndays]
        nd.append(100000*(di - di1)/(ndays*pop))
        dates2.append(dates[i])
        # print(dates[i])
    return dates2, nd

config = get_config()
try:
    status, pops_dict = world_populations()
    assert(status is None)
except Exception as inst:
    print(inst)
    exit(1)

def get_county_weekly(df, pop):
    """ Generate lists or arrays of x and y values for a single nation based on daily change averaged over seven days

    Args:
        df Dataframe for a nation

    Returns:
        Pandas date-time index of weekly dates (array-like)
        Array of average daily deaths per 100,000 people
    """
    ndays=7
    l = len(df)
    i1 = (l-1) % ndays
    deaths = df.deaths
    dates = df.index.get_level_values('date')
    nd =[]
    dates2 =[]
    for i in range(i1,l,ndays):
        di = deaths[i]
        di1 = deaths[i-ndays]
        nd.append(100000*(di - di1)/(ndays*pop))
        dates2.append(dates[i])
    return dates2, nd

# Main
start = time.time()

config = get_config()
try:
    status, pops_dict = world_populations()
    assert(status is None)
except Exception as inst:
    print(inst)
    exit(1)
status, df=get_world_covid_jh()
dmax = df.index.get_level_values('date').max()

#Make it a whole number of weeks
df = df[df.index.get_level_values('date') > dmax-np.timedelta64(int(config['PLOT CONFIGURATION']['calendar_window'])*7*24,'h')]

#get us data
df_us=df[df.index.get_level_values('ISO_A3')=='USA']
df_us=df_us.groupby(axis='index', by=['date']).sum()

#populations of countries
pop = pops_dict['USA']['population']
dates_n, nd_nation = get_nation_weekly(df_us, pop)

#prepare to look up country names
upload_time=0
df = df[df.index.get_level_values('ISO_A3')=='USA'].reset_index().set_index(['date'])
nfigs = 0
for fips in df.fips.unique():
        print(fips)

        #get weekly data
        df_county=df[df.fips ==fips]
        county = df_county.iloc[0].county
        state = df_county.iloc[0].state

        #weekly changes
        pop = df_county.population.iloc[0]
        if pop != 0:
            dates,nd = get_county_weekly(df_county, pop)

            #make plot
            MAX_Y = 10*float(config['PLOT CONFIGURATION']['max_y'])
            fig, ax=plt.subplots(figsize=(4.5,2.4), constrained_layout=True)
            plt.xticks(fontsize=9)
            ax.set_ylim(0,  MAX_Y)
            for tick in ax.get_xticklabels():
                tick.set_rotation(45)
            ax.plot(dates, nd)
            ax.plot(dates_n, nd_nation)
            ax.legend([county + ' County, ' + state, 'USA'], fontsize=9)
            pop = int(pop)
            spop = "{:,}".format(pop)
            ax.set_title(f'Daily New Fatalities per 100,000 Population ({spop})', fontsize=9)

            #Put text showing last date and last value
            last = len(nd)-1
            last_date=f'{dates[last]}'[:10]
            ax.annotate(f'{last_date}, {round(nd[last],3)}', [dates[last],nd[last]], fontsize=9)

            #save and upload
            start_up = time.time()
            fig.savefig(config['FILES']['scratch_image'])
            if config['SWITCHES']['send_content_to_local_html'] != '0':
                fig.savefig('/var/www/html/' + fips + '.jpg')
            plt.close()
            send_content(config['FILES']['scratch_image'], 'covid.phoenix-technical-services.com', fips + '.jpg', title=fips, show_progress=True)
            os.remove(config['FILES']['scratch_image'])
            upload_time += time.time()-start_up
            nfigs += 1
end = time.time()
seconds = round(end-start)
print(f'\nCounty plots made. {nfigs} figures uploaded. Upload time: {round(upload_time,2)}. Elapsed time: {str(datetime.timedelta(seconds=seconds))}')