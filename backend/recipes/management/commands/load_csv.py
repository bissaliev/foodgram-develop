import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

# from pathlib import Path


BASE_DIR = settings.BASE_DIR
# DIRECTORY = Path(BASE_DIR).parent.joinpath("data")
file_name = "ingredients.csv"


class Command(BaseCommand):
    help = "Load data from csv file to model"

    def load_Ingredients(self):
        file = os.path.join(os.path.dirname(BASE_DIR), "data", file_name)
        with open(file, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            Ingredient.objects.all().delete()
            for row in reader:
                print(row)
                Ingredient.objects.create(name=row[0], measurement_unit=row[1])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Ингредиент {row[0]} добавлен в модель."
                    )
                )
            self.stdout.write(
                self.style.SUCCESS("Записи полностью добавлены!")
            )

    def handle(self, *args, **options):
        self.load_Ingredients()
