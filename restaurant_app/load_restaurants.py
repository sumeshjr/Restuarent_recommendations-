import csv
from django.core.management.base import BaseCommand
from .models import Restaurant

class Command(BaseCommand):
    help = 'Load restaurant data from CSV file'

    def handle(self, *args, **kwargs):
        with open('zomato.csv', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Restaurant.objects.get_or_create(
                    restaurant_name=row['restaurant name'],
                    restaurant_type=row['restaurant type'],
                    rate=float(row['rate (out of 5)']) if row['rate (out of 5)'] else 0,
                    num_of_ratings=int(row['num of ratings']) if row['num of ratings'] else 0,
                    avg_cost=float(row['avg cost (two people)']) if row['avg cost (two people)'] else 0,
                    online_order=row['online_order'].lower() == 'yes',
                    table_booking=row['table booking'].lower() == 'yes',
                    cuisines_type=row['cuisines type'],
                    area=row['area'],
                    local_address=row['local address']
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded restaurant data'))
