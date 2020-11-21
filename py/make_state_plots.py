"""Generate and upload raster images of covid plots, one for each state. This stand-alone program
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

def get_state_weekly(df):
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

#populations of states
pop = pops_dict['USA']['population']
dates, nd = get_nation_weekly(df_us, pop)

df = df[df.index.get_level_values('ISO_A3')=='USA'].reset_index().set_index(['date'])
df.drop(['ISO_A3', 'country_name', 'lat', 'lon', 'cases', 'fips', 'county', 'isos2', 'isos3', 'code3', 'FIPs', 'Admin2', 'country_region', 'latitude', 'longitude', 'combined_key'], axis='columns')
states_fips_s = df.state_fips.unique()
pops_dict = csv_get_dict(config['FILES']['state_census'], 0, 1, header=True)
df_states = df.groupby(['date','state_fips', 'state']).sum()
for fips in states_fips_s:

        #get weekly data
        df_state=df_states[df_states.index.get_level_values('state_fips') ==fips]
        state = df_state.index.get_level_values('state')[0]
        if fips == '17':
            print("hello")
        df_state=df_state.resample('W', level='date', closed='right').last()


        #Avoid partial weeks
        y=df_state[:len(df_state)-1].index.get_level_values('date').max()
        if dmax-y != np.timedelta64(24*7,'h'):
            df_state=df_state[:len(df_state)-1]
            
        #weekly changes
        dates_n,nd_state = get_state_weekly(df_state)

        #make plot

     c
        fig, ax=plt.subplots()
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
        ax.plot(dates_n, nd_state)
        ax.plot(dates, nd)
        ax.set_ylim(0, MAX_Y)
        ax.legend([state, 'USA'])
        ax.set_title('Daily New Fatalities per 100,000 Population')

        #Put text showing last date and last value
        last = len(nd_state)-1
        last_date=f'{dates_n[last]}'[:10]
        ax.annotate(f'{last_date}, {round(nd_state[last],4)}', [dates_n[last],nd_state[last]])
        fig.tight_layout(pad=4)

        #save and upload
        start = time.time()
        fig.savefig(config['FILES']['scratch_image'])
        plt.close()
        upload_file(config['FILES']['scratch_image'], 'phoenix-technical-services.com', fips + '.jpg', title=fips)
        os.remove(config['FILES']['scratch_image'])