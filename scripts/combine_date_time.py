from sale.models import Bill
from datetime import datetime


def combine():
    bills = Bill.objects.all()
    for bill in bills:
        bill.generated_at = datetime.combine(bill.date, bill.time)
        bill.save()

combine()