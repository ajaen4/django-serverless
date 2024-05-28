# Generated by Django 5.0.2 on 2024-05-27 08:12

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Operator",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Coverage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "location",
                    django.contrib.gis.db.models.fields.PointField(srid=4326),
                ),
                ("g2", models.BooleanField()),
                ("g3", models.BooleanField()),
                ("g4", models.BooleanField()),
                (
                    "operator_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="operators.operator",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["operator_id"],
                        name="operators_c_operato_664902_idx",
                    ),
                    models.Index(
                        fields=["location"],
                        name="operators_c_locatio_facbdb_idx",
                    ),
                    models.Index(
                        fields=["operator_id", "location"],
                        name="operators_c_operato_561308_idx",
                    ),
                ],
            },
        ),
    ]
