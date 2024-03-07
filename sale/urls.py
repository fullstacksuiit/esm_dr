from django.urls import path
from sale import views

urlpatterns = [
    path("bill/active/", views.active_bills, name="active_bills"),
    path("bill/form", views.bill_form, name="bill_form"),
    path("invoice/<int:bill_id>", views.invoice, name="invoice"),
    path("bill/", views.bill, name="bill"),
    path("menu/", views.menu, name="menu"),
    path("order_menu/", views.order_menu, name="order_menu"),
    path("dish/", views.dish, name="dish"),
    path("feedback/", views.feedback, name="feedback"),
    path("review/", views.review, name="review"),
    path("history/", views.sale_history, name="sale_history"),
    path("csv_report/", views.csv_report, name="csv_report"),
    path("udhaar/", views.udhaar_table, name="udhaar"),
    path("udhaar/update/", views.update_udhaar, name="udhaar_update"),
    path("dish/new", views.new_dish, name="new_dish"),
    path("dish/update/<int:dish_id>", views.update_dish, name="update_dish"),
    path("kot/history", views.kot_history, name="kot_history"),
    path("kot/<int:kot_id>", views.kot, name="kot"),
    path("", views.order, name="order"),
]

