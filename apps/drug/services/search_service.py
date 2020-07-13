from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import models


class PostgresFulltextSearch:
    model_objects_manager: models.Manager = None
    fields_config: [] = None

    def __init__(self, model_objects_manager: models.Manager, natural_sorting_field: str = 'id', fields_config=None):
        self.model_objects_manager = model_objects_manager
        self.natural_sorting_field = natural_sorting_field

        if fields_config is None:
            self.fields_config = [
                {
                    "field_name": "name",
                    "weight": "A"
                }

            ]
        else:
            self.fields_config = fields_config

    def search(self, keyword):
        return self.search_terms(keyword)

    def search_terms(self, keyword):
        """
        searching in term
        fulltext search based on SearchQuery and SearchVector and ranking on it
        :param keyword:
        :return:
        """
        first_field = self.fields_config[0]
        combined_search_vector = SearchVector(first_field.get('field_name'), weight=first_field.get('weight'))
        for index, field_config in enumerate(self.fields_config):
            if index == 0:
                continue
            combined_search_vector += SearchVector(field_config.get('field_name'), weight=field_config.get('weight'))

        search_query = SearchQuery(keyword)

        # search
        res = self.model_objects_manager \
            .annotate(search=combined_search_vector) \
            .filter(search=search_query)
        # rank based search result
        res = res \
            .annotate(rank=SearchRank(combined_search_vector, search_query)) \
            .order_by('-rank',
                      '-{}'.format(self.natural_sorting_field))
        return res
