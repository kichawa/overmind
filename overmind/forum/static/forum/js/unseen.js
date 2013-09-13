(function ($) {

  $.fn.markUnseenTopics = function (options) {
    var o = $.extend({}, $.fn.markUnseenTopics.defaults, options);

    var dfd = $.getJSON(options.apiUrl);

    return this.each(function () {
      var $el = $(this),
          tid = parseInt($el.attr(o.idAttr), 10),
          updated = new Date(Date.parse($el.attr(o.updatedAttr)));

      $el.html(o.pendingHTML);
      dfd.done(function (data) {
        data.last_seen_all = new Date(Date.parse(data.last_seen_all));
        var lastSeen = data.last_seen_all;
        if (data.seen_topics[tid]) {
          var seenDate = new Date(Date.parse(data.seen_topics[tid]));
          if (seenDate > lastSeen) {
            lastSeen = seenDate;
          }
        }
        if (lastSeen < updated) {
          $el.html(o.unseenHTML);
        } else {
          $el.html(o.seenHTML);
        }
      });
    });
  };

  $.fn.markUnseenTopics.defaults = {
    apiUrl: null,
    idAttr: 'data-topic-id',
    updatedAttr: 'data-topic-updated',
    pendingHTML: '...',
    seenHTML: 'old',
    unseenHTML: 'new'
  };

}(jQuery));
