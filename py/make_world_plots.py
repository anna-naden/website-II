"""Generate and upload raster images of covid plots, one for each nation. This stand-alone program
runs nightly

"""
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import datetime
from filelock import FileLock

from get_world_covid_jh import get_world_covid_jh
from world_populations import world_populations
from send_content import send_content
from get_config import get_config
from csv_util import csv_get_dict

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
    i1 = (l-1)%ndays
    for i in range(i1,l,ndays):
        di = deaths[i]
        di1 = deaths[i-ndays]
        nd.append(100000*(di - di1)/(ndays*pop))
        dates2.append(dates[i])
        # print(di,di1,di-di1)
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
ISO_A3_codes = df.index.get_level_values('ISO_A3').unique()
df = df[df.index.get_level_values('date') > dmax-np.timedelta64(int(config['PLOT CONFIGURATION']['calendar_window'])*7*24,'h')]

#get us data
df_us=df[df.index.get_level_values('ISO_A3')=='USA']
df_us=df_us.groupby(axis='index', by=['date']).sum()

#populations of countries
pop = pops_dict['USA']['population']
dates, nd = get_nation_weekly(df_us, pop)

#prepare to look up country names
countries = csv_get_dict(config['FILES']['nation_props'], 0, 1)
upload_time=0
nfigs = 0
for ISO_A3 in ISO_A3_codes:
    if ISO_A3 in countries.keys():

        #get weekly data
        df_nation=df[df.index.get_level_values('ISO_A3')==ISO_A3]
        df_nation=df_nation.groupby(axis='index', by=['date']).sum()
        df_nation = df_nation[df_nation.index.get_level_values('date') > dmax-np.timedelta64(39*7*24,'h')]

        pop = pops_dict[ISO_A3]['population']
        #weekly changes
        dates_n,nd_nation = get_nation_weekly(df_nation, pop)

        #make plot
        fig, ax=plt.subplots(figsize=(3,3), constrained_layout=True)
        ax.set_ylim(0, float(config['PLOT CONFIGURATION']['max_y']))
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
        ax.plot(dates_n, nd_nation)
        ax.plot(dates, nd)
        ax.legend([countries[ISO_A3].replace('_',','), 'USA'])
        spop = "{:,}".format(pop)
        ax.set_title(f'Daily Fatalities per 100,000 Pop. ({spop})', fontsize=9)

        #Put text showing last date and last value
        last = len(nd_nation)-1
        last_date=f'{dates_n[last]}'[:10]
        x = dates_n[last]
        y = nd_nation[last]
        ax.annotate(f'{last_date}, {round(nd_nation[last],4)}', [x,y], 
            xycoords='data',
            xytext=(dates_n[last-20],y+.5), textcoords='data',
            arrowprops=dict(arrowstyle="->"))

        #save and upload
        start_upload = time.time()
        if config['SWITCHES']['send_content_to_local_html'] != '0':
            fig.savefig('/var/www/html/' + ISO_A3 + '.jpg')

        lock = FileLock(config['FILES']['lockfile'])
        with lock:
            fig.savefig(config['FILES']['scratch_image'])
            send_content(config['FILES']['scratch_image'], 'covid.phoenix-technical-services.com', ISO_A3 + '.jpg', title=ISO_A3)
            os.remove(config['FILES']['scratch_image'])
        plt.close()
        upload_time += time.time()-start_upload
        nfigs += 1
end = time.time()
seconds = round(end-start)
print(f'\nWorld plots made: {nfigs} figures uploaded. Upload time: {round(upload_time,2)}. Elapsed time: {str(datetime.timedelta(seconds=seconds))} secs.')