from django.urls import path

from apps.drug.views import (ListCreateDrugView, RetrieveDrugView,
                             ListCreateDrugCategoriesView, ListCreatePharmaciesView, ListCreatePrescriptionView,
                             ListPrescriptionDetailView, PatchPrescriptionView, RetrieveUpdateCategoryView,
                             RetrieveUpdatePharmacyView, RetrievePrescriptionView, SendMailPrescriptionView,
                             BulkCreateDrugView)
from apps.drug.views_statistic import (
    PharmacyPrescriptionStatisticView, CommonPrescriptionStatsView, PharmaciesPrescriptionStatisticView)

# urls

urlpatterns = [
    path('common-stats-date/', CommonPrescriptionStatsView.as_view(),
         name='common-stats-date'),
    path('pharmacies/prescription/stats/', PharmaciesPrescriptionStatisticView.as_view(),
         name='pharmacies-prescription-stats'),
    path('drugs/', ListCreateDrugView.as_view(), name='list-create-drug'),
    path('drugs/bulk/', BulkCreateDrugView.as_view(), name='bulk-create-drug'),
    path('drugs/<uuid:pk>/', RetrieveDrugView.as_view(), name='retrieve-drug'),
    path('drugs/categories/', ListCreateDrugCategoriesView.as_view(), name='list-create-categories'),
    path('drugs/categories/<uuid:pk>/', RetrieveUpdateCategoryView.as_view(), name='retrieve-update-category'),
    # path('drugs/aggregation/', AggregateDrugCategoryView.as_view(), name='drugs-aggregation'),
    path('pharmacies/', ListCreatePharmaciesView.as_view(), name='list-create-pharmacies'),
    path('pharmacies/<uuid:pk>/', RetrieveUpdatePharmacyView.as_view(), name='retrieve-update-pharmacy'),
    path('pharmacies/<uuid:pk>/prescription-stats/', PharmacyPrescriptionStatisticView.as_view(),
         name='pharmacy-prescription-stats'),
    path('prescription/', ListCreatePrescriptionView.as_view(), name='list-create-prescription'),
    path('prescription/<uuid:pk>/', RetrievePrescriptionView.as_view(), name='retrieve-prescription'),
    path('prescription/<uuid:pk>/details/', ListPrescriptionDetailView.as_view(), name='list-prescription-detail'),
    path('prescription/<uuid:pk>/changes/', PatchPrescriptionView.as_view(), name='list-prescription-changes'),
    path('prescription/<uuid:pk>/mail/', SendMailPrescriptionView.as_view(), name='mail-prescription')
]
