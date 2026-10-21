from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class Produce(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

   

    def __str__(self):
        return self.name    

