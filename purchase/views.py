from os import name
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required

from datetime import datetime
from django.db.models import Sum, Avg

from .models import Purchase, Supplier, Item
from .serializers import SupplierSerializer


@login_required
def purchase(request):
    if request.method == "GET":
        suppliers = Supplier.objects.all()
        context = {"suppliers": suppliers}
        return render(request, "purchase.html", context)
    elif request.method == "POST":
        total_amount = 0
        print(request.POST)
        supplier = Supplier.objects.get(id=request.POST.get("supplier").upper())
        items = request.POST.getlist("item")
        amounts = request.POST.getlist("amount")
        rate = request.POST.getlist("rate")
        quantities = request.POST.getlist("quantity")
        date = request.POST.get("date")
        pur = Purchase(date=date, supplier=supplier)
        pur.save()
        for i in range(len(items)):
            item = items[i]
            amount = round(float(amounts[i]), 2)
            it = Item(
                amount=amount,
                rate=float(rate[i]),
                item=item,
                quantity=quantities[i],
                purchase=pur,
            )
            it.save()
            total_amount += amount
        pur.total_amount = total_amount
        pur.save()

        return HttpResponse("SUCCESS")


@login_required
@api_view(http_method_names=["GET", "POST"])
def supplier(request):
    if request.method == "GET":
        sup = SupplierSerializer(
            get_object_or_404(Supplier, id=request.query_params.get("id"))
        )
        return Response(sup.data, status=status.HTTP_200_OK)
    if request.method == "POST":
        sup = SupplierSerializer(data=request.data)
        sup.is_valid(raise_exception=True)
        sup.save()
        return Response(sup.data, status=status.HTTP_201_CREATED)


@login_required
@api_view(http_method_names=["GET"])
def all_suppliers(request):
    if request.method == "GET":
        sup = SupplierSerializer(Supplier.objects.all(), many=True)
        return Response(sup.data, status=status.HTTP_200_OK)


@login_required
def purchase_history(request):
    now = datetime.now()

    if request.method == "POST":
        start_date = request.POST.get("from")
        end_date = request.POST.get("to")
        if start_date and end_date:
            # if both dates are present, so we have a date window. startdate>=results<=enddate
            purc = Purchase.objects.filter(date__gte=start_date, date__lte=end_date)
        elif start_date:
            #  if only the start_date is provided. The resulted queryset will extend till today.
            purc = Purchase.objects.filter(date__gte=start_date)
        elif end_date:
            # queryset will contain results till the enddate
            purc = Purchase.objects.filter(date__lte=end_date)
        else:
            purc = Purchase.objects.filter(date=now)

    else:
        # Query to get bills of the present day.
        purc = Purchase.objects.filter(date=now)

    sale = purc.aggregate(Avg("total_amount"), Sum("total_amount"))
    avg = sale["total_amount__avg"]
    total_sale = sale["total_amount__sum"]

    if avg and total_sale:
        avg = round(avg, 2)
        total_sale = round(total_sale, 2)

    context = {
        "purchases": purc,
        "total_sale": total_sale,
        "avg": avg,
    }

    return render(request, "purchase_history.html", context)
