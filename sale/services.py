from datetime import datetime
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from sale.models import Bill, Order, Dish, KOT



def create_kot(data, bill):
    kot = KOT(details=data, bill=bill)
    kot.save()
    return kot

def generate_kot(request, kot_id):
    kot = KOT.objects.get(id=kot_id)
    context = {"orders": kot.details, "table": kot.bill.table_no}
    return render(request, "kot_bill.html", context)


def generate_active_kots():
    return KOT.objects.filter(bill__kot_status=True).order_by("-created_at")


def create_order(request):
    rp = request.POST
    table = rp.get("table")
    try:
        bill = Bill.objects.get(table_no=table, kot_status=True)
    except ObjectDoesNotExist:
        bill = Bill(table_no=table)
        bill.save()
    items = rp.getlist("item_id")
    plates = rp.getlist("plate")
    quantities = rp.getlist("quantity")
    dishes = []
    for i in range(len(items)):
        dish = Dish.objects.get(id=items[i])
        data = {
            "bill_id": bill,
            "dish": dish,
            "quantity": quantities[i],
            "size": plates[i],
        }
        try:
            order_obj = Order.objects.get(dish=dish, bill_id=bill, size=data["size"])
        except ObjectDoesNotExist:
            order_obj = Order(**data)
        else:
            order_obj.quantity += int(data["quantity"])
        order_obj.save()
        order_data = {
            "dish_name": dish.name,
            "quantity": quantities[i],
            "size": plates[i],
        }
        dishes.append(order_data)
    return bill, dishes


def filter_invoices(start_date, end_date, order_type, payment_type):
    today = datetime.now()
    bills = Bill.objects.filter(kot_status=False)
    orders = Order.objects.all()
    if order_type == "ALL":
        order_type = None
    if payment_type == "ALL":
        payment_type = None
    if not start_date and not end_date:
        bills = bills.filter(date=today)
        orders = orders.filter(bill_id__date=today)
    else:
        if start_date:
            bills = bills.filter(date__gte=start_date)
            orders = orders.filter(bill_id__generated_at__gte=start_date)
        if end_date:
            bills = bills.filter(date__lte=end_date)
            orders = orders.filter(bill_id__generated_at__gte=end_date)
    if order_type:
        bills = bills.filter(order_type=order_type)
    if payment_type:
        bills = bills.filter(payment_type=payment_type)
    orders = Order.objects.filter(bill_id__in=bills)
    return bills, orders
