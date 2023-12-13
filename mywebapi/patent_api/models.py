from django.db import models


# Create your models here.
class Patent(models.Model):
    ano = models.CharField(max_length=20)
    title = models.TextField()
    abstract = models.TextField()
    apos = models.TextField()
    ipcs = models.TextField()
    featurewords = models.TextField()
    probs = models.TextField()
    year = models.IntegerField()
    country = models.CharField(max_length=20)
    province = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
