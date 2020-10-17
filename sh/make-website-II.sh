# -------- Get Johns Hopkins dataset ----------------------
cd ~/Downloads
rm -rf COVID-19
git clone https://github.com/CSSEGISandData/COVID-19.git
cp COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv ~/datasets/covid-19
cp COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv ~/datasets/covid-19
cp COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv ~/datasets/covid-19
cp COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv ~/datasets/covid-19

# ---------- Create and serialize dataframe
conda activate website-II
cd ~/projects/website-II/py
python make_pickle.py

# ---------- Extract 30-day fatalities to json and js files, upload to s3
python make_county_features.py
python make_states_features.py
python make_world_features.py

# -------------------------------------------------------------
# Upload content
#--------------------------------------------------------------
~/projects/website-II/sh/upload-s3.sh