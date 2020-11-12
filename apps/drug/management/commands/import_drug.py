import csv
from random import randint

from django.core.management.base import BaseCommand

from apps.drug.models import Drug, Category
from apps.drug.services.prescription_excel_generation import PrescriptionExcelGeneration


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _create_tags(self):

        file_path = './apps/drug/management/commands/drug.csv'

        objs = []

        categories = Category.objects.all()

        with open(file_path, newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            i = 0
            for row in reader:
                i += 1
                if i == 101:
                    break
                name = row.get('drugName', None)
                rate = row.get('rating', 0)
                rate = float(rate)
                index_cat = randint(0, len(categories) - 1)
                category = categories[index_cat]
                price = randint(50000, 1000000)
                if name is None:
                    continue
                objs.append(Drug(name=name, rate=rate, category=category, price=price))

        Drug.objects.bulk_create(objs)
        print('import drugs successfully')
        return

    def _init_category(self):
        categories = Category.objects.all()
        if len(categories) > 0:
            print('categories exists')
        else:
            list_categories = [
                'gây mê',
                'trị đau lưng và chăm sóc giảm nhẹ',
                'chống dị ứng và phản vệ,'
                'giải độc và các chất giải độc khác',
                'chống co giật',
                'chống bệnh truyền nhiễm',
                'đau nửa đầu',
                'chống khối u và ức chế miễn dịch',
                'parkinson',
                'ảnh hưởng đến máu',
                'sản phẩm máu và thay thế huyết tương',
                'tim mạch',
                'da liễu',
                'tẩy uế và sát trùng',
                'lợi niệu',
                'dạ dày ruột',
                'hormone, nội tiết, tránh thai',
                'giãn cơ',
                'mắt',
                'khác'
            ]
            new_categories = [Category(name=name) for name in list_categories]

            Category.objects.bulk_create(new_categories)
            print('initialized successfully')

        return

    def handle(self, *args, **options):
        han = PrescriptionExcelGeneration('f9ecae20-9c17-4a36-b642-657c329b451a')
        han.exec()
        # self._init_category()
        # self._create_tags()
