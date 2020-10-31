from abc import ABC
from datetime import datetime

from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import InvalidFilterException
from apps.drug.models import Drug, Category, Pharmacy, Prescription, PrescriptionDetail, WorkSpace, UserWorkSpace
from apps.drug.serializers import (
    DrugSerializer, DrugCategorySerializer, PharmacySerializer, PrescriptionDetailSerializer,
    SendMailPrescriptionSerializer, BulkCreateDrugSerializer, PharmacyDetailSerializer,
    PrescriptionUpdateDetailSerializer, PrescriptionDrugContentSerializer, DrugDetailSerializer,
    PrescriptionDrugContentDetailSerializer)
from apps.drug.services.search import PostgresFulltextSearch, CONFIG_PRESCRIPTION_RANK, CONFIG_DRUG_RANK


# Create your views here.

class WorkSpaceParamView(ABC):

    def get_work_space(self, ws_id):
        try:
            user = self.request.user  # noqa
            work_space = WorkSpace.objects.get(id=ws_id)
            UserWorkSpace.objects.get(work_space=work_space, user=user)
            return work_space
        except WorkSpace.DoesNotExist or UserWorkSpace.DoesNotExist:
            raise generics.ValidationError(f"Work Space {ws_id} does not exist")


class ListCreateDrugView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Drug.objects.all()

    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search by name, condition""",
                                type=openapi.TYPE_STRING)
    price_from = openapi.Parameter('price_from', in_=openapi.IN_QUERY,
                                   description="""Price from""",
                                   type=openapi.TYPE_NUMBER)
    price_to = openapi.Parameter('price_to', in_=openapi.IN_QUERY,
                                 description="""Price to""",
                                 type=openapi.TYPE_NUMBER)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return DrugSerializer
        return DrugDetailSerializer

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
            q_list = [Q(key__icontains=keyword), Q(name__icontains=keyword)]
            search_handler = PostgresFulltextSearch(query_set, CONFIG_DRUG_RANK)
            return search_handler.search(keyword, q_list)

        return query_set.order_by('-modified')

    @swagger_auto_schema(operation_description='Get list drugs', manual_parameters=[keyword, price_from, price_to])
    def get(self, request, *args, **kwargs):
        return super(ListCreateDrugView, self).get(request, *args, **kwargs)


class RetrieveUpdateDestroyDrugView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DrugSerializer
    queryset = Drug.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return DrugDetailSerializer
        return DrugSerializer


class ListCreateDrugCategoryView(generics.ListCreateAPIView):
    serializer_class = DrugCategorySerializer
    queryset = Category.objects.all()
    permission_classes = (IsAuthenticated,)

    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search by name""",
                                type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Get list categories', manual_parameters=[keyword])
    def get(self, request, *args, **kwargs):
        return super(ListCreateDrugCategoryView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword', None)
        if keyword:
            return Category.objects.filter(name__icontains=keyword).order_by('-created')
        return Category.objects.all().order_by('-created')


class RetrieveUpdateCategoryView(generics.RetrieveUpdateAPIView):
    serializer_class = DrugCategorySerializer
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()


class ListCreatePharmacyView(WorkSpaceParamView, generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Pharmacy.objects.all()
    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search by name""",
                                type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Get list pharmacies', manual_parameters=[keyword])
    def get(self, request, *args, **kwargs):
        return super(ListCreatePharmacyView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword', None)
        ws = self.get_work_space(self.kwargs.get('work_space_id'))
        base_cond = Q(work_space=ws)
        if keyword:
            return Pharmacy.objects.filter(base_cond).filter(name__icontains=keyword).order_by('-created')
        return Pharmacy.objects.filter(base_cond).order_by('-created')

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PharmacySerializer
        return PharmacyDetailSerializer


class RetrieveUpdatePharmacyView(WorkSpaceParamView, generics.RetrieveUpdateAPIView):
    queryset = Pharmacy.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PharmacyDetailSerializer
        return PharmacySerializer

    def get_object(self):
        ws = self.get_work_space(self.kwargs.get("work_space_id"))
        try:
            return Pharmacy.objects.get(work_space=ws, id=self.kwargs.get("pk"))
        except Pharmacy.DoesNotExist:
            raise generics.ValidationError(f'pharmacy {self.kwargs.get("pk")} does not exist.')


class ListCreatePrescriptionView(WorkSpaceParamView, generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Prescription.objects.all()

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
        ws = self.get_work_space(self.kwargs.get("work_space_id"))

        date = self.request.GET.get('date', None)
        keyword = self.request.query_params.get('keyword', None)

        if not date and not keyword:
            return Prescription.objects.filter(work_space=ws).order_by('-created')

        query_set = Prescription.objects.filter(work_space=ws)

        if date:
            dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")

            start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            end = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            query_set = query_set.filter(
                created__gte=start,
                created__lte=end
            )

        if keyword:
            search_handler = PostgresFulltextSearch(query_set, CONFIG_PRESCRIPTION_RANK, 'created')
            q_list = [Q(name__icontains=keyword), Q(status__icontains=keyword)]
            return search_handler.search(keyword, q_list)

        return query_set.order_by('-created')

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return PrescriptionDetailSerializer
        return PrescriptionDrugContentSerializer


class RetrieveDestroyPrescriptionView(WorkSpaceParamView, generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Prescription.objects.all()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return PrescriptionDetailSerializer
        return PrescriptionUpdateDetailSerializer

    def get_object(self):
        ws = self.get_work_space(self.kwargs.get("work_space_id"))
        try:
            return Prescription.objects.get(work_space=ws, id=self.kwargs.get("pk"))
        except Prescription.DoesNotExist:
            raise generics.ValidationError(f"Prescription {self.kwargs.get('pk')} does not exist")


class PrescriptionDrugContentDetailView(WorkSpaceParamView, generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PrescriptionDrugContentDetailSerializer
    queryset = Prescription.objects.all()

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)

        key_sort = None

        field_sort = self.request.query_params.get('active', None)
        direction = self.request.query_params.get('direction', None)

        if field_sort == 'name':
            key_sort = 'drug__name'
        if field_sort == 'price':
            key_sort = 'price_at_the_time'
        if field_sort == 'available':
            key_sort = 'is_available'

        if key_sort:
            if direction == 'desc':
                key_sort = f'-{key_sort}'
            return PrescriptionDetail.objects.filter(prescription__id=pk).order_by(key_sort)
        return PrescriptionDetail.objects.filter(prescription__id=pk).order_by('created')


class PrescriptionDrugContentUpdateView(WorkSpaceParamView, generics.UpdateAPIView):
    serializer_class = PrescriptionDrugContentSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Prescription.objects.all()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_object(self):
        ws = self.get_work_space(self.kwargs.get("work_space_id"))
        try:
            return Prescription.objects.get(work_space=ws, id=self.kwargs.get("pk"))
        except Prescription.DoesNotExist:
            raise generics.ValidationError(f"Prescription {self.kwargs.get('pk')} does not exist.")


class BulkCreateActionDrugView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=BulkCreateDrugSerializer)
    def post(self, request, *args, **kwargs):
        serializer = BulkCreateDrugSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = serializer.bulk_create()
        return Response(res)


class SendMailPrescriptionView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        prescription_id = self.kwargs.get('pk')
        serializer = SendMailPrescriptionSerializer(data={"prescription_id": prescription_id})
        serializer.is_valid(raise_exception=True)
        return Response({})
