#!/bin/bash

for file in index.html county-time-series2.html us-hot2.html state-hot.html us-hot2-m.html world-m.html world.html
do
    aws s3 cp /var/www/html/$file s3://covid.phoenix-technical-services.com --acl public-read
done

for file in make_state_map.js make_us_map.js make_world_map.js map_colors.js make_world_map_m.js make_us_map_m.js
do
    aws s3 cp /home/anna_user2/Dropbox/projects/website-II/js/$file s3://covid.phoenix-technical-services.com/js/$file --acl public-read
done

# aws s3 cp /home/anna_user2/projects/website-II/static/stylesheets/style.css s3://phoenix-technical-services.com/stylesheets/style.css --acl public-read
aws s3 cp /home/anna_user2/Dropbox/projects/website-II/static/stylesheets/style.css s3://covid.phoenix-technical-services.com/stylesheets/style.css --acl public-read
