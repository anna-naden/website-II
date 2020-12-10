// get color depending on feature data value
function getColor(d) {
    return d > 10 ? '#003f5c' :
            (d > 5  ? '#2f4b7c' :
            (d > 2.5  ? '#665191' :
            (d > 1.25  ? '#a05195' :
            (d > .625   ? '#d45087' :
            (d > .3125   ? '#f95d6a' :
            (d > .15625   ? '#ff7c43' :
                        '#ffa600'))))));
}

function map_grades() {
    return [0, .15625, .3125, .625, 1.25, 2.5, 5, 10];
}