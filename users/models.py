# users/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
# add additional fields in here
	username = models.CharField(('User ID'), max_length=30, unique = True)
	email = models.EmailField(('email address'),blank = True)
	firstname =  models.CharField(('first name'),max_length=30,blank = True)
	lastname = models.CharField(('last name'),max_length=30,blank = True)
	avatar = models.ImageField(('image'),default = "default.jpeg",blank = True,upload_to = "profile_pics")

	def __str__(self):
		return self.username

	USERNAME_FIELD = 'username'
	
def contact_default():
    return {"firstname": "Webmaster",
            "lastname":"Sumanyu"}

class Relationship(models.Model):

	class Meta:
		unique_together=(('active_id','receiver_id'),)

	active_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
	receiver_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="friend")
	#relationship_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	#use default_field id as foreign key
	net_balance = models.IntegerField(default=0)

class Group(models.Model):
	grp_name = models.CharField(max_length=30)
	members = models.ManyToManyField(CustomUser)

class Transaction(models.Model):

	active_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="trans_name")
	#transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	amt_paid = models.IntegerField(default=0)
	group_or_no = models.BooleanField(default=False)
	settling_or_no = models.BooleanField(default=False)
	group_num = models.ForeignKey(Group,null=True,blank=True,on_delete=models.CASCADE)
	trans_name = models.CharField(max_length=60)
	date = models.DateTimeField(default=timezone.now, blank=True)
	CHOICES=(('Other','Other'),('Work','Work'),('Personal','Personal'))
	trans_tag=models.CharField(max_length=10,null=True,choices=CHOICES)


class Accounts(models.Model):

	class Meta:
		unique_together=(('trans_id','relation_id'),)

	trans_id=models.ForeignKey(Transaction,on_delete=models.CASCADE)
	relation_id=models.ForeignKey(Relationship,on_delete=models.CASCADE)
	amt_exchanged=models.IntegerField(default=0)









