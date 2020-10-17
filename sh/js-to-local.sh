#!/bin/bash

for file in barchart.js make_time_series.js make_state_map.js make_us_map.js make_world_map.js
do
    cp /home/anna_user2/projects/website-II/js/$file /var/www/html/js
done