from django.db import models


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


class UserSearch(models.Model):
    user_id = models.IntegerField()
    search_word = models.CharField(max_length=255)
    distribution_conclusion = models.TextField()
    innovation_conclusion = models.TextField()
    network_conclusion = models.TextField()
    wordcloud_base64 = models.TextField()
    word_network_base64 = models.TextField()
