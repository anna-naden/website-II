// get color depending on feature data value
function getColor(d, max_level) {
    return d > max_level ? '#003f5c' :
            (d > max_level/2  ? '#2f4b7c' :
            (d > max_level/4  ? '#665191' :
            (d > max_level/8  ? '#a05195' :
            (d > max_level/16   ? '#d45087' :
            (d > max_level/32   ? '#f95d6a' :
            (d > max_level/64   ? '#ff7c43' :
                        '#ffa600'))))));
}

function map_grades(max_level) {
    return [0, max_level/64, max_level/32, max_level/16, max_level/8, max_level/4, max_level/2, max_level]
    // return [0, .15, .3, .6, 1.2, 2.4, 4.8, 9.6];
}