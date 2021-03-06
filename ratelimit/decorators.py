from __future__ import absolute_import

from functools import wraps

from django.http import HttpRequest, HttpResponse

from ratelimit import ALL, UNSAFE
from ratelimit.utils import is_ratelimited


__all__ = ['ratelimit']


def ratelimit(group=None, key=None, rate=None, method=ALL, block=False):
    def decorator(fn):
        @wraps(fn)
        def _wrapped(*args, **kw):
            # Work as a CBV method decorator.
            if isinstance(args[0], HttpRequest):
                request = args[0]
            else:
                request = args[1]
            request.limited = getattr(request, 'limited', False)
            ratelimited = is_ratelimited(request=request, group=group, fn=fn,
                                         key=key, rate=rate, method=method,
                                         increment=True)
            if ratelimited and block:
                return HttpResponse(
                    'HTTP Error 429: Too Many Requests. There are an unusual number of requests coming from this IP address {ip_address}. Let\'s discover our plans in the Fever mobile app.'.format(ip_address=request.META.get('REMOTE_ADDR')),
                    status=429
                )
            return fn(*args, **kw)
        return _wrapped
    return decorator


ratelimit.ALL = ALL
ratelimit.UNSAFE = UNSAFE
