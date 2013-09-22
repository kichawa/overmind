import json

from django.http import HttpResponse
from django.views.generic.base import View

from counter import backend



class CounterView(View):
    def __init__(self):
        self.cache = backend.default()

    def json_response(self, request, resp, status=200):
        return HttpResponse(json.dumps(resp), content_type='application/json',
                            status=status)


class Main(CounterView):
    def get(self, request):
        keys = request.REQUEST.getlist('key')
        resp = self.cache.get(*keys)
        return self.json_response(request, resp)

    def post(self, request):
        # we don't support multiple values for one key
        pairs = dict(request.POST.items())
        if pairs:
            resp = self.cache.set(**pairs)
        return self.json_response(request, resp, 201)


class Increment(CounterView):
    def put(self, request):
        try:
            keys = json.loads(request.body.decode('utf8'))
        except ValueError:
            return self.json_response(request, {'error': 'Invalid json'}, 400)
        resp = self.cache.increment(*keys)
        return self.json_response(request, resp)


class Decrement(CounterView):
    def put(self, request):
        try:
            keys = json.loads(request.body.decode('utf8'))
        except ValueError:
            return self.json_response(request, {'error': 'Invalid json'}, 400)
        resp = self.cache.decrement(*keys)
        return self.json_response(request, resp)
