from datetime import datetime

from django.db.models import Sum

from apps.drug.config import CANCELLED_KEY, DONE_KEY, IN_PROGRESS_KEY
from apps.drug.models import Prescription, WorkSpace


class CommonPrescriptionStatsService:

    def __init__(self, work_space: WorkSpace, date):
        self.date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")
        self.work_space = work_space

    def get_total_number_prescription(self):
        """
        get number of total prescription
        """
        return Prescription.objects.filter(work_space=self.work_space, created__gte=self.date).count()

    def get_total_number_prescription_cancelled(self):
        """
        CANCELLED
        """
        return Prescription.objects.filter(work_space=self.work_space,
                                           created__gte=self.date,
                                           status=CANCELLED_KEY).count()

    def get_total_number_prescription_done(self):
        """
        DONE
        """
        return Prescription.objects.filter(work_space=self.work_space,
                                           created__gte=self.date,
                                           status=DONE_KEY).count()

    def get_total_money_prescription(self):
        res = Prescription.objects.filter(work_space=self.work_space,
                                          created__gte=self.date,
                                          status__in=[DONE_KEY, IN_PROGRESS_KEY]
                                          ).annotate(money=Sum('total_price')).first()
        money = res.money if res and res.money else 0
        return money
