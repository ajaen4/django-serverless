import csv
from typing import Tuple

from django.core.management.base import BaseCommand
from operators.models import Operator, Coverage
from django.contrib.gis.geos import Point


class Command(BaseCommand):
    help = "Initiliazes DB. Idempotent, only runs if it hasn't been initialized yet."

    def handle(self, *args: Tuple, **options: dict) -> None:
        if not Operator.objects.exists():
            Command.load_operators()
            init_data = Command.read_init_data(
                "data/operators_cvg_processed.csv"
            )
            Command.load_coverage_bulk(init_data)
            self.stdout.write(
                self.style.SUCCESS("Successfully initialized DB")
            )
        else:
            self.stdout.write(self.style.SUCCESS("DB already initialized"))

    @staticmethod
    def load_operators() -> None:
        operators = [
            Operator(id=20801, name="Orange"),
            Operator(id=20810, name="SFR"),
            Operator(id=20815, name="Free"),
            Operator(id=20820, name="Bouygue"),
        ]
        Operator.objects.bulk_create(operators)

    @staticmethod
    def read_init_data(path: str) -> list[dict]:
        init_data = list()
        with open(path) as f:
            reader = csv.DictReader(f)
            init_data = [row for row in reader]
        return init_data

    @staticmethod
    def load_coverage_bulk(data: list[dict]) -> None:
        operators_cvg = list()
        for operator_cvg in data:
            operator_id = operator_cvg["operator_id"]
            operator_cvg.pop("operator_id")
            location = Point(
                float(operator_cvg["longitude"]),
                float(operator_cvg["latitude"]),
                srid=4326,
            )
            operator_cvg.pop("latitude")
            operator_cvg.pop("longitude")

            operators_cvg.append(
                Coverage(
                    operator_id=Operator.objects.get(id=operator_id),
                    location=location,
                    **operator_cvg
                )
            )
        Coverage.objects.bulk_create(operators_cvg)
