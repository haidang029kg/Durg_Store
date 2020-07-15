from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.drug.models import Pharmacy
from apps.drug.serializers_statistic import (
    PharmacyPrescriptionStatisticSerializer, PharmaciesPrescriptionStatisticSerializer)
from apps.drug.services.common_prescription_stats import CommonPrescriptionStatsService


class PharmacyPrescriptionStatisticView(generics.RetrieveAPIView):
    serializer_class = PharmacyPrescriptionStatisticSerializer
    queryset = Pharmacy.objects.all()
    permission_classes = (IsAuthenticated,)

    type = openapi.Parameter('type', in_=openapi.IN_QUERY,
                             description="""date time type [DAYS, MONTHS, YEARS]""",
                             type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='GET Pharmacy Prescription Stats', manual_parameters=[type])
    def get(self, request, *args, **kwargs):
        return super(PharmacyPrescriptionStatisticView, self).get(request, *args, **kwargs)


class PharmaciesPrescriptionStatisticView(APIView):
    serializer_class = PharmaciesPrescriptionStatisticSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=PharmaciesPrescriptionStatisticSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = serializer.get_stats()
        return Response(res)


class CommonPrescriptionStatsView(APIView):
    permission_classes = (IsAuthenticated,)

    date = openapi.Parameter('date', in_=openapi.IN_QUERY,
                             description="""Date common stats format %Y-%m-%d""",
                             type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='GET Prescription Stats By Date', manual_parameters=[date])
    def get(self, request, *args, **kwargs):
        date = self.request.query_params.get('date', None)
        if not date:
            raise ValidationError('date is required', status.HTTP_400_BAD_REQUEST)

        handler = CommonPrescriptionStatsService(date)

        total_pres_works = handler.get_total_number_prescription()
        total_pres_cancelled = handler.get_total_number_prescription_cancelled()
        total_pres_done = handler.get_total_number_prescription_done()
        money = handler.get_total_money_prescription()
        return Response({
            'total_pres_works': total_pres_works,
            'total_pres_done': total_pres_done,
            'total_pres_cancelled': total_pres_cancelled,
            'money': money
        })
