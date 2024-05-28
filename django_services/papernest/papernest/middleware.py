from django.http import HttpResponse, HttpRequest
from django.utils.deprecation import MiddlewareMixin


class HealthCheckMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest) -> HttpResponse:
        if request.META["PATH_INFO"] == "/ping/":
            return HttpResponse("OK")
