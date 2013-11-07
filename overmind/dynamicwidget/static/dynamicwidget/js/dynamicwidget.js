(function ($) {


  var lockName = '__withLockSentinel__';
  // wrap function to make sure any other call will be dropped till `done`
  // callback is called
  var withLock = function (fn) {
    var wrapper = function () {
      if (fn.hasOwnProperty(lockName)) {
        return;
      }
      fn[lockName] = true;
      var done = function () {
        delete fn[lockName];
      };
      var args = Array.prototype.slice.call(arguments);
      args.unshift(done);
      return fn.apply(this, args);
    };
    wrapper.name = fn.name;
    return wrapper;
  };


  // wrap function to ensure it's context
  var wrapfn = function (ctx, fn) {
    var wrapper = function () {
      var args = Array.prototype.slice.call(arguments);
      return fn.apply(ctx, args);
    };
    wrapper.name = fn.name;
    return wrapper;
  };



  // for given list of widget names (wids), fetch content from the server and
  // load using given $el scope
  var loadWidgets = function ($el, attrName, wids) {
    var chunks = [];

    $.each(wids, function (_, wid) {
        chunks.push('wid=' + wid);
    });


    var parseResponse = function ($el, data) {
      // check if name is vali jQuery method and try to call
      $.each(data, function (name, args) {
        if ($.isFunction($el[name])) {
          if ($.isArray(args)) {
            $el[name].apply($el, args);
          } else {
            $el[name].call($el, args);
          }
        }
      });
    };


    var done = $.Deferred();

    $.getJSON(window.DYNAMIC_WIDGETS_URL + '?' + chunks.join('&'), function (resp) {
      $.each(resp, function (wid, data) {
        if (data.error && console && console.warn) {
          console.warn("dynamic widget error:", data.error);
        }


        // check if given element is a widget container
        if ($el.attr(attrName) === wid) {
          parseResponse($el, data);
        } else {
          // find all inside given element
          $el.find('[' + attrName + '="' + wid + '"]').each(function () {
            parseResponse($(this), data);
          });
        }
      });
      done.resolve();
    });

    return done;
  };


  // for given $el selector, find all [dw-load] elements and load content for
  // them, according to name set with this attribute
  var widgetsLoadContent = function ($el) {
    var wids = [];
    $el.find('[dw-load]').each(function () {
      wids.push($(this).attr('dw-load'));
    });
    loadWidgets($el, 'dw-load', wids);
  };


  var initializeDynamicWidgets = function () {
    var $doc = $(document);

    $doc.on('mouseenter', '[dw-hover]', withLock(function (done) {
      var $el = $(this);
      var wid = $el.attr('dw-hover');
      loadWidgets($el, 'dw-hover', [wid]).done(function () {
        $el.removeAttr('dw-hover');
        done();
      });
    }));

    $doc.on('click', '[dw-click]', withLock(function (done) {
      var $el = $(this);
      var wid = $el.attr('dw-click');
      loadWidgets($el, 'dw-click', [wid]).done(function () {
        $el.removeAttr('dw-click');
        done();
      });
    }));

    widgetsLoadContent($doc);
  };



  $(function () {
    if (!window.DYNAMIC_WIDGETS_URL) {
      return;
    }
    initializeDynamicWidgets();
  });

}(jQuery));
