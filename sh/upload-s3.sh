#!/bin/bash

# for file in index.html barchart.html county-time-series2.html us-hot2.html state-hot.html ISO-A3-time-series2.html election.html
# do
#     aws s3 cp /var/www/html/$file s3://phoenix-technical-services.com --acl public-read
# done

for file in index.html barchart.html county-time-series2.html us-hot2.html state-hot.html election.html
do
    aws s3 cp /var/www/html/$file s3://covid.phoenix-technical-services.com --acl public-read
done

# for file in barchart.js make_time_series.js make_state_map.js make_us_map.js make_world_map.js
# do
#     aws s3 cp /home/anna_user2/projects/website-II/js/$file s3://phoenix-technical-services.com/js/$file --acl public-read
# done

for file in barchart.js make_state_map.js make_us_map.js make_world_map.js
do
    aws s3 cp /home/anna_user2/projects/website-II/js/$file s3://covid.phoenix-technical-services.com/js/$file --acl public-read
done

# aws s3 cp /home/anna_user2/projects/website-II/static/stylesheets/style.css s3://phoenix-technical-services.com/stylesheets/style.css --acl public-read
aws s3 cp /home/anna_user2/projects/website-II/static/stylesheets/style.css s3://covid.phoenix-technical-services.com/stylesheets/style.css --acl public-read
