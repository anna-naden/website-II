conda activate website-II

# -------- Get Johns Hopkins dataset ----------------------
cd ~/Downloads
rm -rf COVID-19
git clone https://github.com/CSSEGISandData/COVID-19.git
cp COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv ~/datasets/covid-19
cp COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv ~/datasets/covid-19
cp COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv ~/datasets/covid-19
cp COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv ~/datasets/covid-19

#Transform csv to Data Frame pickle
cd /home/anna_user2/projects/website-II/py
python make_pickle2.py
if [ $? -ne 0 ]
then
    exit 1
fi

# ---------- Make and upload jpeg files for coumty stats plots
python make_county_plots.py
if [ $? -ne 0 ]
then
    exit 1
fi
xecho 'County plots made'