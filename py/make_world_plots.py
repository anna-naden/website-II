import numpy as np
import matplotlib.pyplot as plt
import os

from get_world_covid_jh import get_world_covid_jh
from world_populations import world_populations
from s3_util import upload_file
from get_config import get_config

def get_nation_weekly(df, pop):
    ndays=7
    l = len(df)
    nc=np.zeros(l)
    nd=np.zeros(l)
    nds=np.zeros(l)
    cases = df.cases
    deaths = df.deaths

    for i in range(1,l):
        ci = cases[i]
        ci1 = cases[i-1]

        di = deaths[i]
        di1 = deaths[i-1]

        nc[i] = ci - ci1
        nd[i] = di - di1

    nc = 100000*nc/(ndays*pop)
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
ISO_A3_codes = df.index.get_level_values('ISO_A3').unique()
df_us=df[df.index.get_level_values('ISO_A3')=='USA']
df_us=df_us.groupby(axis='index', by=['date']).sum()
df_us=df_us.resample('W', level='date').first()

pop = pops_dict['USA']['population']
dates, nd = get_nation_weekly(df_us, pop)
for ISO_A3 in ISO_A3_codes:
    # print(ISO_A3)
    df_nation=df[df.index.get_level_values('ISO_A3')==ISO_A3]
    df_nation=df_nation.groupby(axis='index', by=['date']).sum()
    df_nation=df_nation.resample('W', level='date').first()
    pop = pops_dict[ISO_A3]['population']
    dates,nd_nation = get_nation_weekly(df_nation, pop)
    if len(dates)==len(nd):
        plt.plot(dates,nd)
        fig, ax=plt.subplots()
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
        ax.plot(dates, nd_nation)
        ax.plot(dates, nd)
        ax.legend([ISO_A3, 'USA'])
        ax.set_title('Daily New Fatalities per 100,000 Population')
        fig.tight_layout(pad=4)
        fig.savefig(config['FILES']['scratch_image'])
        plt.close()
        upload_file(config['FILES']['scratch_image'], 'phoenix-technical-services.com', ISO_A3 + '.jpg', title=ISO_A3)
        os.remove(config['FILES']['scratch_image'])
