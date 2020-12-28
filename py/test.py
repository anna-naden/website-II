"""Make JSON strings for leaflet choropleth maps and d3 graphs of
monthly COVID deaths by county. Upload to S3

"""

import os

import numpy as np
import json
import pandas as pd
import csv
import time
import datetime

from send_content import send_content
from get_world_covid_jh import get_world_covid_jh
from get_config import get_config

config = get_config()
with open('temp.json', 'rt') as f:
    feature_string = f.read()

features = json.loads(feature_string)
