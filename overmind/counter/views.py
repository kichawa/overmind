import json

from django.http import HttpResponse

from . import backend


def get_counter(request):
    cache = backend.default()
    resp = cache.get(*request.GET.getlist('key'))
    return HttpResponse(json.dumps(resp), content_type='application/json',
                        status=200)
