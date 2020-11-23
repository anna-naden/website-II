"""Generate and upload raster images of covid plots, one for each nation. This stand-alone program
runs nightly

"""
import numpy as np
import matplotlib.pyplot as plt
import os
import time

from get_world_covid_jh import get_world_covid_jh
from world_populations import world_populations
from s3_util import upload_file
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
    nc=np.zeros(l)
    nd=np.zeros(l)
    deaths = df.deaths

    for i in range(1,l):
        di = deaths[i]
        di1 = deaths[i-1]
        nd[i] = di - di1
    nd=100000*nd/(ndays*pop)
    
    dates = df.index.get_level_values('date')
    return dates, nd

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

#get us data
df_us=df[df.index.get_level_values('ISO_A3')=='USA']
df_us=df_us.groupby(axis='index', by=['date']).sum()
df_us=df_us.resample('W', level='date', closed='right').last()

#skip partial week at end
y=df_us[:len(df_us)-1].index.get_level_values('date').max()
if dmax-y != np.timedelta64(24*7,'h'):
    df_us=df_us[:len(df_us)-1]

#populations of countries
pop = pops_dict['USA']['population']
dates, nd = get_nation_weekly(df_us, pop)

#prepare to look up country names
countries = csv_get_dict(config['FILES']['nation_props'], 0, 1)
upload_time=0
for ISO_A3 in ISO_A3_codes:
    if ISO_A3 in countries.keys():

        #get weekly data
        df_nation=df[df.index.get_level_values('ISO_A3')==ISO_A3]
        df_nation=df_nation.groupby(axis='index', by=['date']).sum()
        df_nation=df_nation.resample('W', level='date', closed='right').last()

        #Avoid partial weeks
        y=df_nation[:len(df_nation)-1].index.get_level_values('date').max()
        if dmax-y != np.timedelta64(24*7,'h'):
            df_nation=df_nation[:len(df_nation)-1]
            
        pop = pops_dict[ISO_A3]['population']

        #weekly changes
        dates_n,nd_nation = get_nation_weekly(df_nation, pop)

        #make plot
        fig, ax=plt.subplots()
        ax.set_ylim(0, float(config['PLOT CONFIGURATION']['max_y']))
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
        ax.plot(dates_n, nd_nation)
        ax.plot(dates, nd)
        ax.legend([countries[ISO_A3].replace('_',','), 'USA'])
        ax.set_title('Daily New Fatalities per 100,000 Population')

        #Put text showing last date and last value
        last = len(nd_nation)-1
        last_date=f'{dates_n[last]}'[:10]
        ax.annotate(f'{last_date}, {round(nd_nation[last],4)}', [dates_n[last],nd_nation[last]])
        fig.tight_layout(pad=4)

        #save and upload
        start = time.time()
        fig.savefig(config['FILES']['scratch_image'])
        plt.close()
        upload_file(config['FILES']['scratch_image'], 'phoenix-technical-services.com', ISO_A3 + '.jpg', title=ISO_A3)
        os.remove(config['FILES']['scratch_image'])
        upload_time += time.time()-start
print(upload_time)