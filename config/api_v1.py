from django.urls import include, path


urlpatterns = [
    path('', include('apps.drug.urls')),
]
