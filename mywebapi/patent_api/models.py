from django.db import models
from django.contrib.auth.models import User


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    search_word = models.CharField(max_length=255)

    distribution_line_base64 = models.TextField(blank=True, null=True)
    distribution_bar_base64 = models.TextField(blank=True, null=True)
    distribution_conclusion = models.TextField(blank=True, null=True)

    innovation_map_base64 = models.TextField(blank=True, null=True)
    innovation_bar_base64 = models.TextField(blank=True, null=True)
    innovation_conclusion = models.TextField(blank=True, null=True)

    network_base64 = models.TextField(blank=True, null=True)
    network_conclusion = models.TextField(blank=True, null=True)

    wordcloud_base64 = models.TextField(blank=True, null=True)
    word_network_base64 = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ["user", "search_word"]
