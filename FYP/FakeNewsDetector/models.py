from django.db import models
from django.contrib.auth.models import User


class UserInfoModel(models.Model):
    FirstName = models.CharField(max_length=200)
    LastName = models.CharField(max_length=200)
   

class UserLoginModel(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Body(models.Model):
    Text= models.TextField()

    def __str__(self):
        return self.Text
