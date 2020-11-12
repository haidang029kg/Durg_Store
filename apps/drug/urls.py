from django.urls import path

from apps.drug.views import (
    ListCreateDrugView, RetrieveUpdateDestroyDrugView, ListCreateDrugCategoryView, ListCreatePharmacyView,
    ListCreatePrescriptionView, RetrieveUpdateCategoryView, RetrieveUpdatePharmacyView, BulkCreateActionDrugView,
    PrescriptionDrugContentDetailView, PrescriptionDrugContentUpdateView,
    RetrieveDestroyPrescriptionView, SendMailPrescriptionView, GetPrescriptionPdfView)
from apps.drug.views_statistic import (
    PharmacyPrescriptionStatisticView, CommonPrescriptionStatsView, PharmaciesPrescriptionStatisticView)

# urls

urlpatterns = [
    path('drugs/',
         ListCreateDrugView.as_view(),
         name='list-create-drug'),
    path('drugs/bulk-create-action/',
         BulkCreateActionDrugView.as_view(),
         name='bulk-create-drug'),
    path('drugs/<uuid:pk>/',
         RetrieveUpdateDestroyDrugView.as_view(),
         name='retrieve-drug'),
    path('categories/',
         ListCreateDrugCategoryView.as_view(),
         name='list-create-categories'),
    path('categories/<uuid:pk>/',
         RetrieveUpdateCategoryView.as_view(),
         name='retrieve-update-category'),
    path('work-spaces/<uuid:work_space_id>/common-stats-date/',
         CommonPrescriptionStatsView.as_view(),
         name='common-stats-date'),
    path('work-spaces/<uuid:work_space_id>/pharmacies/prescription/stats/',
         PharmaciesPrescriptionStatisticView.as_view(),
         name='pharmacies-prescription-stats'),
    path('work-spaces/<uuid:work_space_id>/pharmacies/',
         ListCreatePharmacyView.as_view(),
         name='list-create-pharmacies'),
    path('work-spaces/<uuid:work_space_id>/pharmacies/<uuid:pk>/',
         RetrieveUpdatePharmacyView.as_view(),
         name='retrieve-update-pharmacy'),
    path('work-spaces/<uuid:work_space_id>/pharmacies/<uuid:pk>/prescription-stats/',
         PharmacyPrescriptionStatisticView.as_view(),
         name='pharmacy-prescription-stats'),
    path('work-spaces/<uuid:work_space_id>/prescription/', ListCreatePrescriptionView.as_view(),
         name='list-create-prescription'),
    path('work-spaces/<uuid:work_space_id>/prescription/<uuid:pk>/',
         RetrieveDestroyPrescriptionView.as_view(),
         name='retrieve-update-destroy-prescription'),
    path('work-spaces/<uuid:work_space_id>/prescription/<uuid:pk>/detail/',
         PrescriptionDrugContentDetailView.as_view(),
         name='list-prescription-drug-detail'),
    path('work-spaces/<uuid:work_space_id>/prescription/<uuid:pk>/pdf/',
         GetPrescriptionPdfView.as_view(),
         name='list-prescription-drug-detail'),
    path('work-spaces/<uuid:work_space_id>/prescription/<uuid:pk>/detail/changes/',
         PrescriptionDrugContentUpdateView.as_view(),
         name='update-prescription-drug-detail'),
    path('work-spaces/<uuid:work_space_id>/prescription/<uuid:pk>/mail/', SendMailPrescriptionView.as_view(),
         name='mail-prescription')
]
