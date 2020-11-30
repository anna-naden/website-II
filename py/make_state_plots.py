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
    deaths = df.deaths
    dates = df.index.get_level_values('date')
    nd =[]
    dates2 =[]
    for i in range(ndays-1,l,ndays):
        di = deaths[i]
        di1 = deaths[i-ndays]
        nd.append(100000*(di - di1)/(ndays*pop))
        dates2.append(dates[i])
        # print(di,di1,di-di1)
    return dates2, nd

def get_state_weekly(df, pop = None):
    """ Generate lists or arrays of x and y values for a single nation based on daily change averaged over seven days

    Args:
        df Dataframe for a nation
        pop int, population (canada only)

    Returns:
        Pandas date-time index of weekly dates (array-like)
        Array of average daily deaths per 100,000 people
    """
    if pop is None:
        pop = df.population.iloc[0]
        if pop == 0:
            print('hello')
    ndays=7
    l = len(df)
    deaths = df.deaths
    dates = df.index.get_level_values('date')
    nd =[]
    dates2 =[]
    for i in range(ndays-1,l,ndays):
        di = deaths[i]
        di1 = deaths[i-ndays]
        nd.append(100000*(di - di1)/(ndays*pop))
        dates2.append(dates[i])
        # print(di,di1,di-di1)
    return dates2, nd

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
df_us = df_us[df_us.index.get_level_values('date') > dmax-np.timedelta64(int(config['PLOT CONFIGURATION']['calendar_window'])*7*24,'h')]

#populations of states
pop = pops_dict['USA']['population']
dates, nd = get_nation_weekly(df_us, pop)

df = df[df.index.get_level_values('ISO_A3')=='USA'].reset_index().set_index(['date'])
df.drop(['ISO_A3', 'country_name', 'lat', 'lon', 'cases', 'fips', 'county', 'isos2', 'isos3', 'code3', 'FIPs', 'Admin2', 'country_region', 'latitude', 'longitude', 'combined_key'], axis='columns')
states_fips_s = df.state_fips.unique()
pops_dict = csv_get_dict(config['FILES']['state_census'], 0, 1, header=True)
df_states = df.groupby(['date','state_fips', 'state']).sum()
MAX_Y = float(config['PLOT CONFIGURATION']['max_y'])
for fips in states_fips_s:

        #get weekly data
        df_state=df_states[df_states.index.get_level_values('state_fips') ==fips]
        state = df_state.index.get_level_values('state')[0]
        df_state = df_state[df_state.index.get_level_values('date') > dmax-np.timedelta64(int(config['PLOT CONFIGURATION']['calendar_window'])*7*24,'h')]

        #weekly changes
        if state in pops_dict.keys():
            dates_n,nd_state = get_state_weekly(df_state, int(pops_dict[state]))

            #make plot
            fig, ax=plt.subplots(figsize=(5,3))
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
            ax.annotate(f'{last_date}, {round(nd_state[last],3)}*', [dates_n[last],nd_state[last]])
            fig.tight_layout(pad=2)

            prior = f'{dates_n[last-1]}'[:10]
            plt.figtext(0.05,0.05,f"*100,000(to date as of {last_date} - to date as of {prior})/(7*population)", fontsize=8)

            #save and upload
            start = time.time()
            fig.savefig(config['FILES']['scratch_image'])
            plt.close()
            upload_file(config['FILES']['scratch_image'], 'covid.phoenix-technical-services.com', fips + '.jpg', title=fips)
            os.remove(config['FILES']['scratch_image'])

################################################################
# Canada
################################################################
status, df = get_world_covid_jh()
province_dict = csv_get_dict(config['FILES']['canada_census'],2,0)

if status is not None:
    exit(1)

df = df[df.index.get_level_values('ISO_A3')=='CAN'].reset_index().set_index(['date'])
df.drop(['ISO_A3', 'country_name', 'lat', 'lon', 'cases', 'fips', 'county', 'isos2', 'isos3', 'code3', 'FIPs', 'Admin2', 'country_region', 'latitude', 'longitude', 'combined_key'], axis='columns')
states_fips_s = df.state_fips.unique()
pops_dict = csv_get_dict(config['FILES']['state_census'], 0, 1, header=True)
df_states = df.groupby(['date','state_fips', 'state']).sum()
MAX_Y = float(config['PLOT CONFIGURATION']['max_y'])
canada_pop_dict = csv_get_dict(config['FILES']['canada_census'],0,1)
for fips in states_fips_s:

        #get weekly data
        df_state=df_states[df_states.index.get_level_values('state_fips') ==fips]
        state = df_state.index.get_level_values('state')[0]
        df_state = df_state[df_state.index.get_level_values('date') > dmax-np.timedelta64(int(config['PLOT CONFIGURATION']['calendar_window'])*7*24,'h')]

        #weekly changes
        if fips in canada_pop_dict.keys():
            pop = int(canada_pop_dict[fips])
            dates_n,nd_state = get_state_weekly(df_state, pop)

            #make plot

            fig, ax=plt.subplots(figsize=(5,3))
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

            prior = f'{dates_n[last-1]}'[:10]
            plt.figtext(0.05,0.05,f"*100,000(to date as of {last_date} - to date as of {prior})/(7*population)", fontsize=8)

            #save and upload
            start = time.time()
            fig.savefig(config['FILES']['scratch_image'])
            plt.close()
            upload_file(config['FILES']['scratch_image'], 'covid.phoenix-technical-services.com', 'CAN' + fips + '.jpg', title='CAN' + fips)
            os.remove(config['FILES']['scratch_image'])