from django.db import connection

from apps.common.logger import logger
from apps.drug.services.calc_bins_from_range_time import BIN_MONTHS, BIN_DAYS, BIN_YEARS


class CalculatePriceByTimeUnitForPharmacy:

    def __init__(self, pharmacy_id, choice, from_date, to_date):
        assert choice in [BIN_MONTHS, BIN_DAYS, BIN_YEARS], 'choice must be in [MONTHS, DAYS, YEARS]'
        self.choice = choice
        self.pharmacy_id = pharmacy_id

        self.from_date = from_date
        self.to_date = to_date

    @property
    def __build_main_query(self):
        query = '''
                SELECT sub.date_fmt, SUM(sub.total_price) as total_price
                FROM (
                    {sub_query}
                ) as sub
                GROUP BY sub.date_fmt;
                '''.format(sub_query=self.__build_sub_query)
        return query

    @property
    def __build_sub_query(self):
        query = '''
                SELECT id, total_price, lateral_date_unit.date_fmt as date_fmt
                FROM drug_prescription
                
                LEFT JOIN LATERAL (
                    SELECT to_char(created, '{date_fmt}') as date_fmt
                ) AS lateral_date_unit ON TRUE
                
                WHERE pharmacy_id = '{pharmacy_id}' AND created BETWEEN '{from_date}' AND '{to_date}'
                ORDER BY date_fmt
                '''.format(date_fmt=self.__get_date_fmt,
                           pharmacy_id=self.pharmacy_id,
                           from_date=self.from_date,
                           to_date=self.to_date)
        return query

    @property
    def __get_date_fmt(self):
        date_fmt = ''

        if self.choice == BIN_DAYS:
            date_fmt = 'YYYY-MM-DD'
        if self.choice == BIN_MONTHS:
            date_fmt = 'YYYY-MM'
        if self.choice == BIN_YEARS:
            date_fmt = 'YYYY'
        return date_fmt

    def run(self):
        query = self.__build_main_query
        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
                res = cursor.fetchall()
                return res
            except Exception as err:
                logger.error('[CalculatePriceByTimeUnit] {}'.format(err))
                raise err


class CalculatePriceByTimeUnitForPharmacies:

    def __init__(self, pharmacy_ids: [str], choice, from_date, to_date):
        assert choice in [BIN_MONTHS, BIN_DAYS, BIN_YEARS], 'choice must be in [MONTHS, DAYS, YEARS]'
        self.choice = choice
        self.pharmacy_ids = pharmacy_ids

        self.from_date = from_date
        self.to_date = to_date

    @property
    def __build_main_query(self):
        query = '''
                   SELECT main_query.pharmacy_id, lateral_pharmacy.name, main_query.date_fmt, main_query.sum_total
                   FROM (
                       SELECT sub_query.pharmacy_id, sub_query.date_fmt, SUM(sub_query.total_price) AS sum_total
                       FROM (
                           {sub_query}
                       ) AS sub_query
                       GROUP BY sub_query.pharmacy_id, sub_query.date_fmt
                       ORDER BY sub_query.pharmacy_id, sub_query.date_fmt
                   ) AS main_query
                   LEFT JOIN 
                    LATERAL (
                        SELECT name
                        FROM drug_pharmacy
                        WHERE drug_pharmacy.id = main_query.pharmacy_id
                   ) AS lateral_pharmacy ON TRUE
                   ;
                   '''.format(sub_query=self.__build_sub_query)
        return query

    @property
    def __build_sub_query(self):
        query = '''
                    SELECT total_price, lateral_date_unit.date_fmt as date_fmt, pharmacy_id
                    FROM drug_prescription

                    LEFT JOIN LATERAL (
                        SELECT to_char(created, '{date_fmt}') as date_fmt
                    ) AS lateral_date_unit ON TRUE

                    WHERE pharmacy_id IN {list_pharmacy_ids} AND created BETWEEN '{from_date}' AND '{to_date}'
                    ORDER BY date_fmt
                    '''.format(date_fmt=self.__get_date_fmt,
                               list_pharmacy_ids=self.__get_list_pharmacy_ids,
                               from_date=self.from_date,
                               to_date=self.to_date)
        return query

    @property
    def __get_list_pharmacy_ids(self):
        res = ["'{}'".format(item) for item in self.pharmacy_ids]
        res = ", ".join(res)
        return '''({})'''.format(res)

    @property
    def __get_date_fmt(self):
        date_fmt = ''

        if self.choice == BIN_DAYS:
            date_fmt = 'YYYY-MM-DD'
        if self.choice == BIN_MONTHS:
            date_fmt = 'YYYY-MM'
        if self.choice == BIN_YEARS:
            date_fmt = 'YYYY'
        return date_fmt

    def run(self):
        query = self.__build_main_query
        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
                res = cursor.fetchall()
                return res
            except Exception as err:
                logger.error('[CalculatePriceByTimeUnitForPharmacies] {}'.format(err))
                raise err
