from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .models import Produce, User

def index(request):
    return render(request, 'index.html')

def produce(request):
    return render(request, 'produce.html')

def login(request):
    return render(request, 'login.html')

@staff_member_required
def dashboard(request):
    context = {
        "produce_count": Produce.objects.count(),
        "customer_count": User.objects.count(),
        "produce_items": Produce.objects.order_by("-pk")[:5],
    }
    return render(request, "dashboard.html", context)