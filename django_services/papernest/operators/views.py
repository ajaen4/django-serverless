from django.views import generic
from django.db.models import QuerySet
from django.http import (
    JsonResponse,
    HttpRequest,
    HttpResponseNotAllowed,
    HttpResponseBadRequest,
)

from .requests import get_coordinates
from .models import Operator, Coverage


class IndexView(generic.ListView):
    template_name = "operators/index.html"
    context_object_name = "operators"

    def get_queryset(self) -> QuerySet[Operator]:
        """Return all operators."""
        return Operator.objects.all()


def operators_cvg(request: HttpRequest) -> JsonResponse:
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    query = request.GET.get("q")
    if query is None:
        return HttpResponseBadRequest("Missing required parameter: 'q'")

    coordinates = get_coordinates(query)
    closest_cvgs = Coverage.get_closest_coverage(coordinates)

    response = dict()
    for cvg in closest_cvgs:
        response[cvg.operator_id.name] = {
            "2G": cvg.g2,
            "3G": cvg.g3,
            "4G": cvg.g4,
        }

    return JsonResponse(response)
