(function ($) {

  var prepareDate = function (date) {
    var dt = new Date(Date.parse(date));
    dt.setMilliseconds(0);
    return dt;
  };

  $.fn.markUnseen = function (options) {
    var o = $.extend({}, $.fn.markUnseen.defaults, options);

    var dfd = $.getJSON(options.apiUrl);

    return this.each(function () {
      var $el = $(this),
          tid = o.id.call($el),
          updated = prepareDate(o.updated.call($el));

      o.whenPending.call($el, tid, updated, o);
      dfd.done(function (data) {
        data.last_seen_all = prepareDate(data.last_seen_all);
        var lastSeen = data.last_seen_all;
        if (data.seen_topics[tid]) {
          var seenDate = prepareDate(data.seen_topics[tid]);
          if (seenDate > lastSeen) {
            lastSeen = seenDate;
          }
        }
        if (lastSeen < updated) {
          o.whenUnseen.call($el, tid, updated, o);
        } else {
          o.whenSeen.call($el, tid, updated, o);
        }
      });
    });
  };

  $.fn.markUnseen.defaults = {
    apiUrl: null,
    id: function () {
      return parseInt($(this).attr('data-topic-id'), 10);
    },
    updated: function () {
      return new Date(Date.parse($(this).attr('data-topic-updated')));
    },
    whenPending: $.noop,
    whenSeen: $.noop,
    whenUnseen: function () {
      $(this).prepend('*');
    }
  };

}(jQuery));
