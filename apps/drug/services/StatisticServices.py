from django.db.models import Count

from apps.common.logger import logger
from apps.drug.models import Drug, Category

# Services


class StatisticServices:

    @staticmethod
    def drug_categories():
        try:
            count_all_drugs = Drug.objects.all().count()

            num_group_by_category = Drug.objects.all().values('category').annotate(total=Count('id'))
            num_group_by_category = list(num_group_by_category)

            categories = Category.objects.all().values('id', 'name')

            for cat in categories:
                try:
                    total_in_cat = next(item for item in num_group_by_category if item['category'] == cat['id'])
                    if total_in_cat:
                        total = total_in_cat['total']
                        per = float(total) / count_all_drugs * 100
                        per = float("{0:.3}".format(per))
                        cat.update({'percentage': per})
                        cat.update({'total': total})
                    else:
                        cat.update({'percentage': None})
                        cat.update({'total': None})
                except Exception as err:
                    cat.update({'percentage': None})
                    cat.update({'total': None})

            res = {
                'number_of_groups': Category.objects.all().count(),
                'number_of_drugs': count_all_drugs,
                'statistic': categories
            }

            return res
        except Exception as e:
            logger.error(e)
            raise e
