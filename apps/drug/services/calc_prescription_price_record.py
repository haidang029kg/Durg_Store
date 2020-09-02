from django.db import connection


class CalculatePrescriptionPriceRecordService:

    @staticmethod
    def calc_total_price_prescription(prescription_id: str) -> float:
        """
        calculate total price of prescription
        :param prescription_id:
        :return:
        """
        query = '''
            SELECT SUM(sub.total_item_price)
            FROM (
                SELECT
                    table_pres_detail.id,
                    table_pres_detail.price_at_the_time * table_pres_detail.quantity as total_item_price
                FROM drug_prescriptiondetail AS table_pres_detail
                WHERE table_pres_detail.prescription_id = '{prescription_id}'
                    AND table_pres_detail.is_available = TRUE
                    AND table_pres_detail.is_removed = FALSE
            ) as sub;
        '''.format(prescription_id=prescription_id)

        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
                res = cursor.fetchone()
                return res[0]
            except Exception as err:
                print(err)
                return None
