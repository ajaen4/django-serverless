import csv

from django.test import TestCase
from django.contrib.gis.geos import Point

from operators.models import Operator, Coverage
from operators.scripts.utils import skip_comments


class CoverageTest(TestCase):
    def setUp(self):
        Operator.objects.create(id=20801, name="Orange")
        Operator.objects.create(id=20810, name="SFR")
        Operator.objects.create(id=20815, name="Free")
        Operator.objects.create(id=20820, name="Bouygue")

        with open("operators/tests/data/operators_cvg_processed.csv") as f:
            reader = csv.DictReader(skip_comments(f))

            for coverage in reader:
                operator_id = coverage["operator_id"]
                coverage.pop("operator_id")
                location = Point(
                    float(coverage["longitude"]),
                    float(coverage["latitude"]),
                    srid=Coverage.SRID_WGS84,
                )
                coverage.pop("latitude")
                coverage.pop("longitude")

                Coverage.objects.create(
                    operator_id=Operator.objects.get(id=operator_id),
                    location=location,
                    **coverage
                )

    def test_get_closest_coverage(self):
        # Three points close to coordinates in DB
        first_coordinates = [2.3289499313178696, 48.86805465377864]
        first_close_cvgs = Coverage.get_closest_coverage(first_coordinates)
        first_expected_results = [
            {
                "operator_id": 20801,
                "location": Point(
                    48.86805465377864,
                    2.329848853894218,
                    srid=Coverage.SRID_WGS84,
                ),
                "g2": True,
                "g3": True,
                "g4": False,
            },
            {
                "operator_id": 20810,
                "location": Point(
                    48.869054544708334,
                    2.3289499313178696,
                    srid=Coverage.SRID_WGS84,
                ),
                "g2": False,
                "g3": False,
                "g4": False,
            },
            {
                "operator_id": 20815,
                "location": Point(
                    48.86805465377864,
                    2.328051008741521,
                    srid=Coverage.SRID_WGS84,
                ),
                "g2": True,
                "g3": False,
                "g4": True,
            },
        ]
        for index, result in enumerate(first_close_cvgs):
            self.assertEqual(
                result.operator_id.id,
                first_expected_results[index]["operator_id"],
            )
            self.assertEqual(
                result.location, first_expected_results[index]["location"]
            )
            self.assertEqual(result.g2, first_expected_results[index]["g2"])
            self.assertEqual(result.g3, first_expected_results[index]["g3"])
            self.assertEqual(result.g4, first_expected_results[index]["g4"])

        # Coordinates out of range of points in DB
        second_coordinates = [-5.073201994866753, 48.45]
        second_close_cvgs = Coverage.get_closest_coverage(second_coordinates)
        self.assertEqual(len(second_close_cvgs), 0)
