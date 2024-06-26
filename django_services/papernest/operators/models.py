from typing import Tuple
from django.db.models import (
    Model,
    IntegerField,
    BooleanField,
    CASCADE,
    ForeignKey,
    CharField,
    Index,
    OuterRef,
    Subquery,
)

from django.db.models.query import QuerySet
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance, Transform


class Operator(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class Coverage(Model):
    SRID_WGS84 = 4326
    SRID_WEB_MERCATOR = 3857
    MAX_DIST_METERS = 200

    operator_id = ForeignKey(Operator, on_delete=CASCADE)
    location = gis_models.PointField(srid=SRID_WGS84)
    g2 = BooleanField()
    g3 = BooleanField()
    g4 = BooleanField()

    def __str__(self) -> str:
        return f"{self.operator_id}, ({self.location.y}, {self.location.x}), {self.g2}, {self.g3}, {self.g4}"

    @classmethod
    def get_closest_coverage(cls, coordinates: Tuple) -> QuerySet["Coverage"]:
        user_location = Point(
            coordinates[1], coordinates[0], srid=cls.SRID_WGS84
        )
        user_location.transform(cls.SRID_WEB_MERCATOR)
        closest_rows = (
            Coverage.objects.annotate(
                transformed_location=Transform(
                    "location", cls.SRID_WEB_MERCATOR
                )
            )
            .annotate(distance=Distance("transformed_location", user_location))
            .filter(distance__lt=cls.MAX_DIST_METERS)
            .order_by("distance")
        )

        min_distance_subquery = (
            closest_rows.filter(operator_id=OuterRef("operator_id"))
            .order_by("distance")
            .values("distance")[:1]
        )

        closest_rows = closest_rows.filter(
            distance=Subquery(min_distance_subquery)
        ).order_by("operator_id", "distance")

        return closest_rows

    class Meta:
        indexes = [
            Index(fields=["operator_id"]),
            Index(fields=["location"]),
        ]
