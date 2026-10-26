from django.contrib.auth.hashers import check_password, make_password
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    items = models.CharField(max_length=255, help_text="What was purchased, e.g. 2kg Tomatoes, 1 tray Eggs")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]

    def __str__(self):
        return f"{self.customer} - {self.amount}"

class Produce(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

   

    def __str__(self):
        return self.name    

