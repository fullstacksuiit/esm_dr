from django.contrib import admin
from sale.models import *

# Register your models here.
admin.site.register([Dish, Bill, Staff, Order, UdharKhata, KOT, Feedback])
