(function () {
    time_picker = $('input#time_picker');
    time_picker.timepicker({
        timeFormat: 'HH:mm:ss',
        interval: 30,
        defaultTime: new Date(0,0,0,8,0,0),
        minTime: new Date(0,0,0,0,0,0),
        maxTime: new Date(0,0,0,23,30,0),
        startTime: new Date(0,0,0,0,0,0)
    });
    $('#set_time').click(function (event) {
        console.log('test');
    });
})();