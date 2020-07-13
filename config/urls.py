"""DrugStore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


class HealthzCheckView(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, *args, **kwargs):
        return Response(status=HTTP_200_OK)


schema_view = get_schema_view(
   openapi.Info(
      title="DRUG STORE API",
      default_version='v1',
      description="Drug store",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="vnhd1995@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz/', HealthzCheckView.as_view(), name='healthz'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('v1/', include('config.api_v1'))
]
