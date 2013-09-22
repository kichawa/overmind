(function ($) {


  $.fn.viewCount = function (options) {
    var o = $.extend({}, $.fn.viewCount.defaults, options);

    var params  = [];
    this.each(function() {
      var tid = o.id.call(this);
      if (tid) {
        params.push('key=' + o.counterKey(tid));
      }
    });
    var dfd = $.getJSON(options.apiUrl + '?' + params.join('&'));

    return this.each(function () {
      var that = this;
      dfd.done(function (resp) {
        var key = o.counterKey(o.id.call(that)),
            value = parseInt(resp[key] || 0, 10);
        o.setCounter($(that), value);
      });
    });
  };


  $.fn.viewCount.defaults = {
    counterKey: function (topicId) {
      return "topic:view:" + topicId;
    },
    id: function () {
      return parseInt($(this).attr('data-topic-id'), 10);
    },
    setCounter: function ($el, value) {
      $el.html(value);
    }
  };


}(jQuery));
