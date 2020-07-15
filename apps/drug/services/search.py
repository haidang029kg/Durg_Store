import operator
from functools import reduce

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import models
from django.db.models import Q

CONFIG_DRUG_RANK = [
    {
        "field_name": "key",
        "weight": "A"
    },
    {
        "field_name": "name",
        "weight": "B"
    }
]

CONFIG_PRESCRIPTION_RANK = [
    {
        "field_name": "name",
        "weight": "A"
    },
    {
        "field_name": "status",
        "weight": "B"
    }
]


class PostgresFulltextSearch:
    model_objects_manager: models.Manager = None
    fields_config: [] = None

    def __init__(self, model_objects_manager: models.Manager, fields_config, natural_sorting_field: str = 'id'):
        self.model_objects_manager = model_objects_manager
        self.natural_sorting_field = natural_sorting_field
        self.fields_config = fields_config

    def search(self, keyword, q_list):
        return self.__search__(keyword, q_list)

    def __search__(self, keyword, q_list):
        """
        fulltext search based on SearchQuery and SearchVector and ranking on it
        :param keyword:
        :return:
        """
        look_up_filter = []
        first_field = self.fields_config[0]
        combined_search_vector = SearchVector(first_field.get('field_name'), weight=first_field.get('weight'))
        for index, field_config in enumerate(self.fields_config):
            look_up_filter.append(Q('{}__icontains={}'.format(field_config.get('field_name'), keyword)))
            if index == 0:
                continue
            combined_search_vector += SearchVector(field_config.get('field_name'), weight=field_config.get('weight'))

        search_query = SearchQuery(keyword)

        res = self.model_objects_manager.filter(reduce(operator.or_, q_list)).annotate(
            rank=SearchRank(combined_search_vector, search_query)
        ).order_by('-rank', '-{}'.format(self.natural_sorting_field))
        return res
