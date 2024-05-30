import csv
import json

from django.test import TestCase
from django.contrib.gis.geos import Point
from django.urls import reverse

from operators.models import Operator, Coverage
from operators.scripts.utils import skip_comments


class OperatorsCvgTest(TestCase):
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
        # Test POST is not available
        first_data = {"q": "42+rue+papernest+75011+Paris"}
        first_response = self.client.post(
            reverse("operators:operators_coverage"), first_data
        )
        self.assertEqual(first_response.status_code, 405)

        # Test correct call
        second_data = {"q": "15 Pl. Vendôme, 75001 Paris, France"}
        second_response = self.client.get(
            reverse("operators:operators_coverage"), second_data
        )
        self.assertEqual(second_response.status_code, 200)

        second_expected_results = {
            "Orange": {
                "2G": True,
                "3G": True,
                "4G": False,
            },
            "SFR": {
                "2G": False,
                "3G": False,
                "4G": False,
            },
            "Free": {
                "2G": True,
                "3G": False,
                "4G": True,
            },
        }
        self.assertEqual(
            json.loads(second_response.content), second_expected_results
        )
