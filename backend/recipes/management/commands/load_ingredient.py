import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.loading_ingredients()

    def loading_ingredients(self, file='ingredients.csv'):
        file_path = f'./data/{file}'
        with open(file_path, newline='', encoding='utf-8') as f:
            read = csv.reader(f)
            for i in read:
                Ingredient.objects.update_or_create(
                    name=i[0],
                    measurement_unit=i[1]
                )
