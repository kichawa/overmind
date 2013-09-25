(function ($) {

  $(function () {
    var chunks = [];
    $('[data-dynamic-widget').each(function () {
      chunks.push('wid=' + $(this).attr('data-dynamic-widget'));
    });

    var url = '/forum/widgets/?' + chunks.join('&');

    $.getJSON(url, function (resp) {
      $.each(resp, function (wid, data) {
        if (data.html) {
          $('[data-dynamic-widget="' + wid + '"]').html(data.html);
        }
      });
    });
  });


}(jQuery));
