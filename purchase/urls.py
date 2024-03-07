from purchase.views import purchase
from django.urls import path

from purchase import views

urlpatterns = [
    path("", views.purchase, name="purchase"),
    path("supplier/", views.supplier, name="supplier"),
    path("supplier/all/", views.all_suppliers, name="all_supplier"),
    path("history/", views.purchase_history, name="purchase_history"),
]
