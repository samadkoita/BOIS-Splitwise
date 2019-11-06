# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # add additional fields in here
    firstname =  models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    def __str__(self):
        return self.email

def contact_default():
    return {"firstname": "Webmaster",
            "lastname":"Sumanyu"}