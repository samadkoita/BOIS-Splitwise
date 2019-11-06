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

class Relationship(models.Model):
	active_id = ForeignKey(CustomUser)
	receiver_id = ForeignKey(CustomUser)
	relationship_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	net_balance = models.IntegerField(default=0)

class Transaction:
	relationship = models.ForeignKey()
	transaction_id = models.UUIDField(default=uuid.uuid4, editable=False)
