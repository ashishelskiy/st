import json
import os
from django.core.management.base import BaseCommand
from service_track_app.models import Product


class Command(BaseCommand):
    help = 'Import products from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file')

    def handle(self, *args, **options):
        json_file = options['json_file']

        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f"File {json_file} does not exist"))
            return

        with open(json_file, 'r', encoding='utf-8') as f:
            products_data = json.load(f)

        created_count = 0
        updated_count = 0

        for product_data in products_data:
            specs = product_data.get('specifications', {})

            product, created = Product.objects.update_or_create(
                name=product_data['model'],
                defaults={
                    'brand': specs.get('Бренд'),
                    'series': specs.get('Серия'),
                    'category': 'subwoofer',
                    'size': specs.get('Размер'),
                    'power_rms': specs.get('Мощность RMS'),
                    'power_max': specs.get('Мощность MAX'),
                    'external_id': product_data.get('product_id'),
                    'external_url': product_data.get('url'),
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f"Created: {product.name}")  # Используем просто name
            else:
                updated_count += 1
                self.stdout.write(f"Updated: {product.name}")  # Используем просто name

        self.stdout.write(
            self.style.SUCCESS(
                f"Import completed! Created: {created_count}, Updated: {updated_count}"
            )
        )