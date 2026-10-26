from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Produce, User as Customer


class CustomerAuthTests(TestCase):
    payload = {
        "firstname": "Casey",
        "lastname": "Grower",
        "username": "casey",
        "email": "casey@example.com",
        "contact": "0700000000",
        "password": "fresh-produce-1",
        "confirm_password": "fresh-produce-1",
    }

    def register(self, **overrides):
        return self.client.post("/register/", {**self.payload, **overrides})

    def test_registration_saves_customer_with_hashed_password(self):
        response = self.register()

        self.assertRedirects(response, "/login/?registered=1")
        customer = Customer.objects.get(username="casey")
        self.assertEqual(customer.email, "casey@example.com")
        self.assertNotEqual(customer.password, "fresh-produce-1")
        self.assertTrue(customer.check_password("fresh-produce-1"))

    def test_registered_customer_can_log_in_by_username_or_email(self):
        self.register()

        for identifier in ("casey", "CASEY@example.com"):
            self.client.post("/logout/")
            response = self.client.post(
                "/login/", {"username": identifier, "password": "fresh-produce-1"}
            )
            self.assertRedirects(response, "/")
            self.assertEqual(
                self.client.session["customer_id"], Customer.objects.get().pk
            )

    def test_wrong_password_is_rejected(self):
        self.register()

        response = self.client.post(
            "/login/", {"username": "casey", "password": "wrong-password"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect username or password.")
        self.assertNotIn("customer_id", self.client.session)

    def test_duplicate_and_invalid_registrations_are_rejected(self):
        self.register()

        duplicate = self.register(email="other@example.com")
        mismatch = self.register(
            username="new", email="new@example.com", confirm_password="different"
        )
        short = self.register(
            username="new2", email="new2@example.com",
            password="short", confirm_password="short",
        )

        self.assertContains(duplicate, "That username is already taken.")
        self.assertContains(mismatch, "Passwords do not match.")
        self.assertContains(short, "at least 8 characters")
        self.assertEqual(Customer.objects.count(), 1)

    def test_navbar_shows_logout_for_signed_in_customer(self):
        self.register()
        self.client.post(
            "/login/", {"username": "casey", "password": "fresh-produce-1"}
        )

        response = self.client.get("/")

        self.assertContains(response, 'action="/logout/"')
        self.assertContains(response, "Log out")
        self.assertNotContains(response, "Get Started")


class DashboardTests(TestCase):
    def test_dashboard_requires_staff_access(self):
        response = self.client.get("/dashboard/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_dashboard_shows_catalog_and_customer_counts(self):
        admin_user = get_user_model().objects.create_user(
            username="farm-admin",
            password="test-password",
            is_staff=True,
        )
        self.client.force_login(admin_user)
        Produce.objects.create(name="Apples", description="Fresh orchard apples")
        Customer.objects.create(
            username="customer-one",
            firstname="Casey",
            lastname="Grower",
            contact="0700000000",
            email="casey@example.com",
            password="not-used-in-dashboard",
        )

        response = self.client.get("/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")
        self.assertEqual(response.context["produce_count"], 1)
        self.assertEqual(response.context["customer_count"], 1)
        self.assertContains(response, "Produce listings")
        self.assertContains(response, "Customer accounts")
        self.assertContains(response, "Apples")
        self.assertContains(response, "Fresh orchard apples")
