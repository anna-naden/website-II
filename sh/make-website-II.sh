# -------- Get Johns Hopkins dataset ----------------------
date

echo 'Downloading Johns Hopkins dataset'
cd ~/Downloads
rm -rf COVID-19
git clone https://github.com/CSSEGISandData/COVID-19.git
cp COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv ~/Dropbox/datasets/covid-19
cp COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv ~/Dropbox/datasets/covid-19
cp COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv ~/Dropbox/datasets/covid-19
cp COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv ~/Dropbox/datasets/covid-19
echo 'Upload done'
date
echo '------------------------------------------------------------------------------------------'

# ---------- Create and serialize dataframe
conda activate website-II
cd ~/Dropbox/projects/website-II/py
python make_pickle2.py
if [ $? -ne 0 ]
then
    exit 1
fi
echo '------------------------------------------------------------------------------------------'

# ---------- Extract 30-day fatalities to json and js files, upload to s3
python make_county_features.py
if [ $? -ne 0 ]
then
   exit 1
fi
echo '------------------------------------------------------------------------------------------'

python make_states_features.py
if [ $? -ne 0 ]
then
    exit 1
fi
echo '------------------------------------------------------------------------------------------'

python make_world_features.py
if [ $? -ne 0 ]
then
    exit 1
fi
echo '------------------------------------------------------------------------------------------'

python make_world_plots.py
if [ $? -ne 0 ]
then
    exit 1
fi
echo '------------------------------------------------------------------------------------------'

python make_state_plots.py
if [ $? -ne 0 ]
then
    exit 1
fi
echo '------------------------------------------------------------------------------------------'

# ---------- Make and upload jpeg files for coumty stats plots
python make_county_plots.py
if [ $? -ne 0 ]
then
    echo 'nonzero fron county plots'
    exit 1
fi
echo 'County plots made'

echo '--------------------------------------------------------------------------------------'
echo 'syncing to s3'
aws s3 sync /var/www/html s3://covid.phoenix-technical-services.com --quiet
echo '---------------------------------------------------------------------------------------'

echo 'Done'
date
