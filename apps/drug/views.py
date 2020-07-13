from datetime import datetime

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import InvalidFilterException
from apps.drug.models import Drug, Category, Pharmacy, Prescription, PrescriptionDetail
from apps.drug.serializers import (DrugSerializers, DrugCategorySerializer, PharmacySerializer, PrescriptionSerializer,
                                   PrescriptionDetailSerializer)
from apps.drug.services.StatisticServices import StatisticServices
# Create your views here.
from apps.drug.services.search_service import PostgresFulltextSearch


class ListCreateDrugView(generics.ListCreateAPIView):
    queryset = Drug.objects.all()
    serializer_class = DrugSerializers
    permission_classes = (AllowAny,)

    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search by name, condition""",
                                type=openapi.TYPE_STRING)
    price_from = openapi.Parameter('price_from', in_=openapi.IN_QUERY,
                                   description="""Price from""",
                                   type=openapi.TYPE_NUMBER)
    price_to = openapi.Parameter('price_to', in_=openapi.IN_QUERY,
                                 description="""Price to""",
                                 type=openapi.TYPE_NUMBER)

    def get_queryset(self):
        query_set = Drug.objects.all()
        price_from = self.request.GET.get('price_from', None)
        price_to = self.request.GET.get('price_to', None)

        if price_from is not None and price_to is not None:
            if float(price_from) > float(price_to):
                raise InvalidFilterException('price filter range is invalid')
            query_set = Drug.objects.filter(price__gte=float(price_from), price__lte=float(price_to))
        else:
            if price_from is not None:
                query_set = Drug.objects.filter(price__gte=float(price_from))
            elif price_to is not None:
                query_set = Drug.objects.filter(price__lte=float(price_to))

        keyword = self.request.query_params.get('keyword', None)
        if keyword:
            search_handler = PostgresFulltextSearch(query_set)
            return search_handler.search(keyword)

        return query_set.order_by('-modified')

    @swagger_auto_schema(operation_description='Get list drugs', manual_parameters=[keyword, price_from, price_to])
    def get(self, request, *args, **kwargs):
        return super(ListCreateDrugView, self).get(request, *args, **kwargs)


class RetrieveDrugView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DrugSerializers
    queryset = Drug.objects.all()
    permission_classes = (AllowAny,)


class ListCreateDrugCategoriesView(generics.ListCreateAPIView):
    serializer_class = DrugCategorySerializer
    queryset = Category.objects.all().order_by('name')
    permission_classes = (AllowAny,)


class RetrieveUpdateCategoryView(generics.RetrieveUpdateAPIView):
    serializer_class = DrugCategorySerializer
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()


class ListCreatePharmaciesView(generics.ListCreateAPIView):
    serializer_class = PharmacySerializer
    queryset = Pharmacy.objects.all().order_by('name')
    permission_classes = (AllowAny,)


class RetrieveUpdatePharmacyView(generics.RetrieveUpdateAPIView):
    serializer_class = PharmacySerializer
    queryset = Pharmacy.objects.all()
    permission_classes = (AllowAny,)


class ListCreatePrescriptionView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = (AllowAny,)
    queryset = Prescription.objects.all().order_by('-created')

    date = openapi.Parameter('date', in_=openapi.IN_QUERY,
                             description="""Search by date created with format %Y-%m-%d""",
                             type=openapi.TYPE_STRING)
    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search by name""",
                                type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Get list prescription', manual_parameters=[date, keyword])
    def get(self, request, *args, **kwargs):
        return super(ListCreatePrescriptionView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        date = self.request.GET.get('date', None)
        keyword = self.request.query_params.get('keyword', None)

        if not date and not keyword:
            return super().get_queryset()

        query_set = Prescription.objects

        if date:
            dt = datetime.strptime(date, '%Y-%m-%d')
            # ~Q(create__date_eq=dt)
            start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            end = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            query_set = query_set.filter(
                created__range=(start, end))

        if keyword:
            search_handler = PostgresFulltextSearch(query_set, 'created', [
                {
                    "field_name": "name",
                    "weight": "A"
                },
                {
                    "field_name": "status",
                    "weight": "B"
                }
            ])
            return search_handler.search(keyword)

        return query_set.all()


class PatchPrescriptionView(generics.UpdateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = (AllowAny,)
    queryset = Prescription.objects.all()


class ListPrescriptionDetailView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PrescriptionDetailSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        return PrescriptionDetail.objects.filter(prescription__id=pk).order_by('-created')


class AggregateDrugCategoryView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        data = StatisticServices.drug_categories()
        return Response(data)
