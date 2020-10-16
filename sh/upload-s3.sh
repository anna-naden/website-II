#!/bin/bash

for file in index.html barchart.html county-time-series.html us-hot2.html world-hot.html state-hot.html
do
    aws s3 cp /var/www/html/$file s3://phoenix-technical-services.com --acl public-read
done

for file in barchart.js make_time_series.js make_state_map.js make_us_map.js make_world_map.js
do
    aws s3 cp /var/www/html/js/$file s3://phoenix-technical-services.com/js/$file --acl public-read
done

aws s3 cp /var/www/html/stylesheets/style.css s3://phoenix-technical-services.com/stylesheets/style.css --acl public-read
