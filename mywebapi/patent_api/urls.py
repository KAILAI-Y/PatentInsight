"""
URL configuration for mywebapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="search"),
    path("result/", views.patent_list, name="patent_list"),
    path("download_csv/", views.download_csv, name="download_csv"),
    path(
        "distribution/",
        views.patent_year_distribution,
        name="patent_year_distribution",
    ),
    path(
        "innovation/",
        views.province_innovation,
        name="province_innovation",
    ),
    path(
        "network/",
        views.network_view,
        name="network_view",
    ),
    path("generate_pdf/", views.generate_pdf, name="generate_pdf"),
]
