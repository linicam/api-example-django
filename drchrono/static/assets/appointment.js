(function () {
    var post = function () {
        var appointment = $(this).parent().attr('id');
        var option = $(this).attr('class');
        console.log(appointment);
        $.ajax({
            url: "/options/",
            method: 'POST',
            data: {
                option: option,
                appointment: appointment
            },
            success:function (result) {
                location.reload()
            },
            error:function (response) {
                console.log(response)
                $('#result').html('result: ' + response.status)
            }
        })
    };
    $('.start').click(post);
    $('.end').click(post)
})();