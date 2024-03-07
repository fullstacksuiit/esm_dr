import requests
from collections import OrderedDict
from base64 import b64encode
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.status import HTTP_202_ACCEPTED

from sale.models import Bill, Dish, Order, UdharKhata, Feedback
from sale.serializers import BillSerializer, OrderSerializer, DishSerializer
from sale.services import (
    create_order,
    filter_invoices,
    create_kot,
    generate_active_kots,
    generate_kot,
)

from datetime import datetime
from django.db.models import Sum, Avg

import pandas

REF_KEY = {
    "RESTAURANT": "R{}",
    "SWIGGY": "S{}",
    "ZOMATO": "Z{}",
}


@api_view(http_method_names=["GET", "POST", "PUT", "PATCH", "DELETE"])
def bill(request):
    if request.method == "GET":
        bill = get_object_or_404(Bill, id=request.query_params.get("bill_id"))
        billser = BillSerializer(bill)
        orders = OrderSerializer(bill.order.all(), many=True)
        return Response(
            {"bill_details": billser.data, "orders": orders.data},
            status=status.HTTP_200_OK,
        )
    elif request.method == "POST":
        bill = BillSerializer(data=request.data)
        bill.is_valid(raise_exception=True)
        bill.save()
        return Response(bill.data, status=status.HTTP_201_CREATED)
    elif request.method in ["PUT", "PATCH"]:
        bill = get_object_or_404(Bill, id=request.data.get("bill_id"))
        bill.kot_status = False
        order_type = request.POST.get("order_type", "RESTAURANT")
        if not bill.ref_no:
            key = REF_KEY[order_type.upper()]
            try:
                latest_bill = Bill.objects.filter(order_type=order_type, ref_no__startswith=key[0], kot_status=False).latest("generated_at")
                last_ref = latest_bill.ref_no[1:]
                new_ref = int(last_ref) + 1
            except Exception:
                new_ref = 1
            finally:
                bill.ref_no = key.format(new_ref)
        if not bill.generated_at:
            bill.generated_at = datetime.now()
        bill.save()
        billser = BillSerializer(bill, data=request.data)
        billser.is_valid(raise_exception=True)
        billser.save()
        if float(request.data.get("amount_due")) > 0:
            previous_amount_due = bill.amount_due
            uk, created = UdharKhata.objects.get_or_create(
                customer=bill.cust_name, contact=bill.contact
            )
            if previous_amount_due > 0 and uk.amount_due > 0:
                uk.amount_due -= previous_amount_due
            uk.amount_due += bill.amount_due
            uk.save()
        return Response(billser.data, status=HTTP_202_ACCEPTED)
    elif request.method == "DELETE":
        bill = get_object_or_404(Bill, id=request.data.get("bill_id"))
        bill.delete()
        return Response({"detail": "Record Deleted"}, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
def active_bills(request):
    if request.method == "GET":
        bill = get_object_or_404(Bill, kot_status=True)
        billser = BillSerializer(bill)
        return Response(
            billser.data,
            status=status.HTTP_200_OK,
        )


@login_required
@csrf_exempt
@api_view(http_method_names=["POST", "PUT", "PATCH", "DELETE", "GET"])
def order(request):
    if request.method == "POST":
        bill, details = create_order(request)
        kot = create_kot(details, bill)
        return generate_kot(request, kot.id)

    elif request.method in ["PUT", "PATCH"]:
        order_obj = get_object_or_404(Order, id=request.data.get("order_id"))
        ordser = OrderSerializer(order_obj, data=request.data)
        ordser.is_valid(raise_exception=True)
        ordser.save()
        return Response(ordser.data, status=HTTP_202_ACCEPTED)

    elif request.method == "DELETE":
        ord = get_object_or_404(Order, id=request.data.get("order_id"))
        ord.delete()
        return Response({"detail": "Record Deleted"}, status=status.HTTP_200_OK)

    elif request.method == "GET":
        active_tables = Bill.objects.filter(kot_status=True).values("table_no", "id")
        dishes = Dish.objects.all()
        context = {"active_tables": active_tables, "dishes": dishes}
        return render(request, "kot.html", context)


@login_required
@api_view(http_method_names=["GET", "POST", "PUT", "PATCH", "DELETE"])
def dish(request):
    if request.method == "GET":
        dish = get_object_or_404(Dish, id=request.query_params.get("dish_id"))
        dishser = DishSerializer(dish)
        return Response(dishser.data, status=status.HTTP_200_OK)
    elif request.method == "POST":
        dish = DishSerializer(data=request.data)
        dish.is_valid(raise_exception=True)
        dish.save()
        return Response(dish.data, status=status.HTTP_201_CREATED)
    elif request.method == "PUT" or request.method == "PATCH":
        dish = get_object_or_404(Dish, id=request.data.get("dish_id"))
        dishser = DishSerializer(dish, data=request.data)
        dishser.is_valid(raise_exception=True)
        dishser.save()
        return Response(dishser.data, status=HTTP_202_ACCEPTED)
    elif request.method == "DELETE":
        dish = get_object_or_404(Dish, id=request.data.get("bill_id"))
        dish.delete()
        return Response({"detail": "Record Deleted"}, status=status.HTTP_200_OK)


@login_required
@api_view(http_method_names=["GET"])
def all_dishes(request):
    if request.method == "GET":
        dish = Dish.objects.all()
        dishser = DishSerializer(dish, many=True)
        return Response(dishser.data, status=status.HTTP_200_OK)


@login_required
def bill_form(request):
    if request.method == "GET":
        return render(request, "bill_form.html")
    elif request.method == "POST":
        request.method = "PUT"
        response = bill(request)
        bill_id = response.data["id"]
        return redirect("invoice", bill_id=bill_id)


def get_payment_qr(bill):
    UPI_ID = "dawatrestaurantrkl@icici"
    amount = f"{bill.amount:.2f}"
    note = f"Bill: {bill.ref_no}, Table: {bill.table_no}"
    res = requests.get(
        "https://upiqr.in/api/qr",
        params={"name": "Daawat", "vpa": UPI_ID, "amount": amount, "note": note},
        timeout=5,
    )
    if res.status_code == 200:
        return b64encode(res.content).decode()


@login_required
def invoice(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    orders = OrderSerializer(bill.order.all(), many=True)

    for order in orders.data:
        if bill.order_type == "RESTAURANT":
            if order["size"] == "full":
                order["price"] = order["dish"]["restaurant_full_price"]
            if order["size"] == "half":
                order["price"] = order["dish"]["restaurant_half_price"]
        elif bill.order_type == "SWIGGY":
            if order["size"] == "full":
                order["price"] = order["dish"]["swiggy_full_price"]
            if order["size"] == "half":
                order["price"] = order["dish"]["swiggy_full_price"]
        elif bill.order_type == "ZOMATO":
            if order["size"] == "full":
                order["price"] = order["dish"]["zomato_full_price"]
            if order["size"] == "half":
                order["price"] = order["dish"]["zomato_half_price"]
    try:
        qr_code = get_payment_qr(bill)
    except Exception:
        qr_code = None
    context = {"bill": bill, "orders": orders.data, "qr": qr_code}
    return render(request, "bill.html", context)




@login_required
def sale_history(request):
    now = datetime.now()

    if request.method == "POST":
        start_date = request.POST.get("from")
        end_date = request.POST.get("to")
        order_type = request.POST.get("order_type")
        payment_type = request.POST.get("payment_type", "ALL")
        bills, orders = filter_invoices(start_date, end_date, order_type, payment_type)
    else:
        # Query to get bills of the present day.
        bills = Bill.objects.filter(date=now, kot_status=False)

    sale = bills.aggregate(Avg("amount"), Sum("amount"))
    avg = sale["amount__avg"]
    total_sale = sale["amount__sum"]

    if avg and total_sale:
        avg = round(avg, 2)
        total_sale = round(total_sale, 2)

    context = {
        "bills": bills.order_by("-generated_at"),
        "total_sale": total_sale,
        "avg": avg,
    }

    return render(request, "billing_history.html", context)


def csv_report(request):
    today = datetime.now()
    if request.method == "POST":
        start_date = request.POST.get("from")
        end_date = request.POST.get("to")
        order_type = request.POST.get("order_type")
        payment_type = request.POST.get("payment_type", "ALL")
        bills, orders = filter_invoices(start_date, end_date, order_type, payment_type)
    else:
        # Query to get bills of the present day.
        bills = Bill.objects.filter(date=today)
        orders = Order.filter(date=today)
    response = HttpResponse(
        content_type="text/csv",
    )
    if request.POST.get("view_type") == "BILLS":
        pandas.DataFrame(
            bills.values(
                "ref_no",
                "date",
                "sub_total",
                "discount",
                "net",
                "cgst",
                "sgst",
                "amount",
            )
        ).to_csv(path_or_buf=response, float_format="%.2f", index=False)
    else:
        pandas.DataFrame(
            orders.values("dish_id__name", "bill_id_id", "quantity", "size")
        ).to_csv(path_or_buf=response, float_format="%.2f", index=False)
    response["Content-Disposition"] = 'attachment; filename="reports.csv"'
    return response


@login_required
def udhaar_table(request):
    context = {}
    context["udhar_khata"] = UdharKhata.objects.all()

    return render(request, "udhaar.html", context)


@csrf_exempt
def update_udhaar(request):
    if request.method == "POST":
        uk = UdharKhata.objects.get(
            customer=request.POST.get("customer"), contact=request.POST.get("contact")
        )
        uk.amount = request.POST.get("amount")
        uk.save()
        return HttpResponse("successful")
    else:
        return HttpResponse("Invalid method")


@login_required
def menu(request):
    dishes = Dish.objects.all().order_by("name")
    context = {"dishes": dishes}
    return render(request, "menu.html", context)


def order_menu(request):
    dishes_qs = Dish.objects.filter(category__isnull=False).values()
    dishes = OrderedDict()
    for dish in dishes_qs:
        if not dish["category"]:
            continue
        category = dish["category"].upper()
        if category not in dishes:
            dishes[category] = []
        dishes[category].append(dish)
    context = {"map": dishes}
    return render(request, "order_menu.html", context)


@login_required
def new_dish(request):
    message = ""
    if request.method == "POST":
        dish = DishSerializer(data=request.POST)
        dish.is_valid(raise_exception=True)
        dish.save()
        message = "Dish {name} added".format(name=request.POST.get("name"))
    categories = Dish.objects.all().values_list("category", flat=True).distinct()
    context = {"message": message, "categories":categories}
    return render(request, "add_dish.html", context)


@login_required
def update_dish(request, dish_id):
    dish = Dish.objects.get(id=dish_id)
    if request.method == "POST":
        dishser = DishSerializer(dish, data=request.POST)
        dishser.is_valid(raise_exception=True)
        dishser.save()
        return redirect("menu")
    context = {"dish": dish}
    return render(request, "update_dish.html", context)


@login_required
def users(request):
    return render(request, "users.html")


@login_required
def kot_history(request):
    kots = generate_active_kots()
    context = {"kots": kots}
    return render(request, "kot_history.html", context)


@login_required
def kot(request, kot_id):
    return generate_kot(request, kot_id)


def feedback(request):
    if request.method == "POST":
        name = request.POST.get('name')
        contact_no = request.POST.get('contact_no')
        bday = request.POST.get('bday')
        ambience = request.POST.get('ambience')
        staff = request.POST.get('staff')
        food_quality = request.POST.get('food_quality')
        review = Feedback(name=name,contact_no=contact_no,bday=bday,ambience=ambience,staff=staff,food_quality=food_quality)
        review.save()
    return render(request, "feedback.html")

@login_required
def review(request):
    reviews = Feedback.objects.all()
    context = {"reviews":reviews }
    return render(request, "review.html", context)
        

