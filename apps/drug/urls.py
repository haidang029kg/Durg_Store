from django.urls import path

from apps.drug.views import (ListCreateDrugView, RetrieveDrugView, AggregateDrugCategoryView,
                             ListCreateDrugCategoriesView, ListCreatePharmaciesView, ListCreatePrescriptionView,
                             ListPrescriptionDetailView, PatchPrescriptionView, RetrieveUpdateCategoryView,
                             RetrieveUpdatePharmacyView)

# urls

urlpatterns = [
    path('drugs/', ListCreateDrugView.as_view(), name='list-create-drug'),
    path('drugs/<uuid:pk>/', RetrieveDrugView.as_view(), name='retrieve-drug'),
    path('drugs/categories/', ListCreateDrugCategoriesView.as_view(), name='list-create-categories'),
    path('drugs/categories/<uuid:pk>/', RetrieveUpdateCategoryView.as_view(), name='retrieve-update-category'),
    path('drugs/aggregation/', AggregateDrugCategoryView.as_view(), name='drugs-aggregation'),
    path('pharmacies/', ListCreatePharmaciesView.as_view(), name='list-create-pharmacies'),
    path('pharmacies/<uuid:pk>', RetrieveUpdatePharmacyView.as_view(), name='retrieve-update-pharmacy'),
    path('prescription/', ListCreatePrescriptionView.as_view(), name='list-create-prescription'),
    path('prescription/<uuid:pk>/details/', ListPrescriptionDetailView.as_view(), name='list-prescription-detail'),
    path('prescription/<uuid:pk>/changes/', PatchPrescriptionView.as_view(), name='list-prescription-changes')
]
