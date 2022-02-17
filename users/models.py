from django.db import models
# from django.contrib.postgres.fields.jsonb import JSONField 
from django.db.models.fields import TextField
# from django.contrib.postgres.fields import JSONField, ArrayField
# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

class Decks(models.Model):
    username = models.CharField(max_length=30)
    name_deck = models.CharField(max_length=50)
    card = models.JSONField(default=list, blank = True)