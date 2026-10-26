from django.contrib.auth import authenticate, login as auth_login
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import Produce, User

CUSTOMER_SESSION_KEY = "customer_id"

def index(request):
    return render(request, 'index.html')

def produce(request):
    return render(request, 'produce.html')

def login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard")
    if request.session.get(CUSTOMER_SESSION_KEY):
        return redirect("customer_dashboard")

    context = {}
    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        admin = authenticate(request, username=identifier, password=password)
        if admin is not None and admin.is_staff:
            auth_login(request, admin)
            return redirect("dashboard")
        customer = (
            User.objects.filter(username__iexact=identifier).first()
            or User.objects.filter(email__iexact=identifier).first()
        )
        if customer and customer.check_password(password):
            request.session.cycle_key()
            request.session[CUSTOMER_SESSION_KEY] = customer.pk
            return redirect("customer_dashboard")
        context["error"] = "Incorrect username or password."
        context["username"] = identifier
    elif request.GET.get("registered"):
        context["success"] = "Account created. Log in to continue."
    return render(request, 'login.html', context)

def register(request):
    if request.session.get(CUSTOMER_SESSION_KEY):
        return redirect("index")

    if request.method != "POST":
        return render(request, "register.html")

    data = {
        field: request.POST.get(field, "").strip()
        for field in ("username", "firstname", "lastname", "contact", "email")
    }
    password = request.POST.get("password", "")
    errors = []

    if not all(data.values()) or not password:
        errors.append("Please fill in every field.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if password != request.POST.get("confirm_password", ""):
        errors.append("Passwords do not match.")
    if User.objects.filter(username__iexact=data["username"]).exists():
        errors.append("That username is already taken.")
    if User.objects.filter(email__iexact=data["email"]).exists():
        errors.append("An account with that email already exists.")

    customer = User(**data)
    if not errors:
        try:
            customer.full_clean(exclude=["password", "username", "email"])
            customer.clean_fields(exclude=["password"])
        except ValidationError as exc:
            errors.extend(m for msgs in exc.message_dict.values() for m in msgs)

    if errors:
        return render(request, "register.html", {"errors": errors, "form": data})

    customer.set_password(password)
    try:
        with transaction.atomic():
            customer.save()
    except IntegrityError:
        return render(request, "register.html", {
            "errors": ["That username or email is already registered."],
            "form": data,
        })
    return redirect("/login/?registered=1")

@require_POST
def logout(request):
    request.session.flush()
    return redirect("index")

def customer_dashboard(request):
    customer = User.objects.filter(pk=request.session.get(CUSTOMER_SESSION_KEY)).first()
    if customer is None:
        request.session.pop(CUSTOMER_SESSION_KEY, None)
        return redirect("login")
    context = {
        "customer": customer,
        "latest_order": customer.orders.first(),
        "produce_count": Produce.objects.count(),
        "produce_items": Produce.objects.order_by("-pk")[:5],
    }
    return render(request, "customer_dashboard.html", context)

@staff_member_required
def dashboard(request):
    context = {
        "produce_count": Produce.objects.count(),
        "customer_count": User.objects.count(),
        "produce_items": Produce.objects.order_by("-pk")[:5],
    }
    return render(request, "dashboard.html", context)