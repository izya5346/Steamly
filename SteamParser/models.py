from django.db import models
from django.db.models.fields import CharField, IntegerField
from django.contrib.postgres.fields import JSONField

class Sticker(models.Model):
    sticker_id = models.IntegerField(unique = True, null = False)
    price = models.IntegerField(null = True)
    name = models.CharField(max_length = 50, null = True)
    icon_url = models.TextField(max_length = 1000, null = True)
class Item(models.Model):
    name = CharField(max_length = 50, null = True)
    default = IntegerField(null = True)
class ItemJson(models.Model):
    data = JSONField()
# Create your models here.
