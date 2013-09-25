import collections
import json

from django.http import HttpResponse

from dynamicwidget import handlers


def widgets(request):
    wids = request.GET.getlist('wid')
    matching_handlers = collections.defaultdict(list)
    result = {}

    # find handlers and group wids by handler function
    for wid in wids:
        fn, params = handlers.default.find(wid)
        if fn:
            matching_handlers[fn].append({'wid': wid, 'params': params})
        else:
            result[wid] = {'error': 'widget "{}" does not exist'.format(wid)}

    # for every widget handler, call it with all related wids at once
    for handler, args in matching_handlers.items():
        result.update(handler(request, args))

    content = json.dumps(result)
    return HttpResponse(content, content_type='application/json')
