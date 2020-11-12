from io import BytesIO

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from apps.drug.models import PrescriptionDetail, Prescription


class PrescriptionPdfGeneration:

    def __init__(self, prescription: Prescription):
        self.__prescription = prescription
        self.__query_set = PrescriptionDetail.objects.select_related('drug') \
            .filter(prescription_id=prescription.id) \
            .order_by('drug__name') \
            .values('drug__name', 'quantity', 'price_at_the_time')

    def generate(self):
        template = get_template('pdf/prescription.html')  # noqa
        items = [{
            "index": index + 1,
            "product_name": item['drug__name'],
            "quantity": item['quantity'],
            "price": f"{int(item['price_at_the_time']):,} vnđ",
            "total_price": f"{int(item['price_at_the_time'] * item['quantity']):,} vnđ",
        } for index, item in enumerate(self.__query_set)]
        ctx = {"items": items,
               "pharmacy_name": self.__prescription.pharmacy.name,
               "address": self.__prescription.pharmacy.address,
               "total_amount": f'{int(self.__prescription.total_price):,} vnđ',
               "date": self.__prescription.created}
        html = template.render(ctx)
        pdf_file_object = BytesIO()
        pisa_status = pisa.pisaDocument(src=BytesIO(html.encode("UTF-8")), dest=pdf_file_object, encoding='UTF-8')
        if not pisa_status.err:
            return HttpResponse(pdf_file_object.getvalue(), content_type='application/pdf')
        return None
