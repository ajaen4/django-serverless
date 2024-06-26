from django.http import HttpResponse, HttpRequest
from django.utils.deprecation import MiddlewareMixin


class HealthCheckMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):
        if request.META["PATH_INFO"] == "/ping/":
            return HttpResponse("OK")
