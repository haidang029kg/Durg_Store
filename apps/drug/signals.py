from django.dispatch import receiver, Signal

from apps.drug.models import Prescription
from apps.drug.services.calc_prescription_price_record import CalculatePrescriptionPriceRecordService

signal_update_or_create_prescription = Signal(providing_args=['prescription_id'])


@receiver(signal_update_or_create_prescription)
def bulk_sync_pharmacy_prescription(**kwargs):
    try:
        prescription_id = kwargs.get('prescription_id')
        ins = Prescription.objects.get(pk=prescription_id)
        total_price = CalculatePrescriptionPriceRecordService.calc_total_price_prescription(prescription_id)
        ins.total_price = total_price if total_price else 0
        ins.save()
    except Exception as err:
        print('signal_update_or_create_prescription SIGNAL: %s' % err)
