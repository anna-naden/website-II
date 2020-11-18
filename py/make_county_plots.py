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

def get_county_weekly(df):
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
    nd=100000*nd/(ndays*df.population)
    
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
df = df[df.index.get_level_values('ISO_A3')=='USA'].reset_index().set_index(['date'])
for fips in df.fips.unique():

        #get weekly data
        df_county=df[df.fips ==fips]
        df_county=df_county.resample('W', level='date', closed='right').last()
        county = df_county.iloc[0].county
        state = df_county.iloc[0].state


        #Avoid partial weeks
        y=df_county[:len(df_county)-1].index.get_level_values('date').max()
        if dmax-y != np.timedelta64(24*7,'h'):
            df_county=df_county[:len(df_county)-1]
            
        #weekly changes
        dates_n,nd_nation = get_county_weekly(df_county)

        #make plot
        fig, ax=plt.subplots()
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
        ax.plot(dates_n, nd_nation)
        ax.plot(dates, nd)
        ax.legend([county + ' County, ' + state, 'USA'])
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
        upload_file(config['FILES']['scratch_image'], 'phoenix-technical-services.com', fips + '.jpg', title=fips)
        os.remove(config['FILES']['scratch_image'])
        upload_time += time.time()-start
print(upload_time)