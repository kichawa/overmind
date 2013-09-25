(function ($) {


  $.fn.dynamicWidget = function (options) {
    var o = $.extend({}, $.fn.dynamicWidget.defaults, options);
    if (!o.url) {
      throw new Error("Cannot fetch widgets. Missing url");
    }

    var chunks = [];
    this.each(function () {
        chunks.push('wid=' + $(this).attr(o.widAttribute));
    });

    var url = o.url + '?' + chunks.join('&');

    $.getJSON(url, function (resp) {
      $.each(resp, function (wid, data) {
        if (data.error && console && console.warn) {
          console.warn("dynamic widget error:", data.error);
        }
        if (data.html) {
          $('[' + o.widAttribute + '="' + wid + '"]').html(data.html);
        }
      });
    });

    return this;
  };


  $.fn.dynamicWidget.defaults = {
    widAttribute: 'data-dynamic-widget',
    url: null
  };

}(jQuery));
