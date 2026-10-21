from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Produce, User as Customer


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
