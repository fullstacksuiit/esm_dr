from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from .views import some_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sale/", include("sale.urls")),
    path("purchase/", include("purchase.urls")),
    path("login/", LoginView.as_view(), name="login"),
    path("", some_view, name="rootview"),
]



admin.site.site_header = 'DAAWAT RESTAURANT'