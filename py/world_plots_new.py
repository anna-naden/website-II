"""Generate and upload raster images of covid plots, one for each nation. This stand-alone program
runs nightly

"""
import numpy as np
import matplotlib.pyplot as plt
import os
import time
from PIL import Image
import numpy as np

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
        fig, ax=plt.subplots(figsize=(5,5))
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
        
        plt.tight_layout(pad=5)

        #Show formula used
        im = Image.open('covid-formula2.png')
        im.resize((32,32))
        im = np.array(im).astype(np.float)/255
        plt.figimage(im,xo=315,yo=275)

        #save and upload
        start = time.time()
        fig.savefig(config['FILES']['scratch_image'])
        plt.close()
        upload_file(config['FILES']['scratch_image'], 'covid.phoenix-technical-services.com', ISO_A3 + '.jpg', title=ISO_A3)
        os.remove(config['FILES']['scratch_image'])
        upload_time += time.time()-start
print(upload_time)