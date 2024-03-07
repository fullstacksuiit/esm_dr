from sale.views import REF_KEY
from sale.models import Bill

def reorder():
    order_types = Bill.OrderType.values
    print(order_types)
    for order_type in order_types:
        bills = Bill.objects.filter(order_type=order_type, kot_status=False).order_by("id")
        key = REF_KEY[order_type]
        for i, bill in enumerate(bills):
            bill.ref_no = key.format(i+1)
            bill.save()


reorder()