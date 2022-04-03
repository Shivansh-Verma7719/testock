from django.db import models
from datetime import datetime

# Create your models here.
class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username =  models.CharField(max_length=255)
    cash = models.FloatField()

class Transactions(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)

    name =models.CharField(max_length=255)
    shares = models.IntegerField()
    price = models.FloatField()
    symbol = models.CharField(max_length=10)
    type = models.CharField(max_length=20)
    time = models.DateTimeField(default = datetime.now, auto_now_add=True)

