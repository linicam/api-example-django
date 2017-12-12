(function () {
    var post = function () {
        $('#result').html('waiting...');
        var appointment = $(this).parent().attr('id');
        var option = $(this).attr('class');
        console.log(appointment);
        $.ajax({
            url: "/appointments/" + appointment + "/actions/",
            method: 'POST',
            data: {
                option: option
            },
            success:function (result) {
                location.reload()
            },
            error:function (response) {
                $('#result').html('result: ' + response.status)
            }
        })
    };
    $('.start').click(post);
    $('.end').click(post)
})();