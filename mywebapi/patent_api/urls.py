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
from django.contrib.auth.views import LogoutView

from .views import (
    index_views,
    search_list_views,
    keyword_networkx_views,
    generate_pdf_views,
    graph_views,
)

urlpatterns = [
    path("", index_views.index, name="index"),
    path("logout/", index_views.logout_view, name="logout"),
    path("result/", search_list_views.patent_list, name="patent_list"),
    path("download_csv/", search_list_views.download_csv, name="download_csv"),
    path(
        "distribution/",
        graph_views.year_distribution,
        name="year_distribution",
    ),
    path(
        "innovation/",
        graph_views.province_innovation,
        name="province_innovation",
    ),
    path(
        "network/",
        graph_views.network_view,
        name="network_view",
    ),
    path(
        "wordcloud/",
        graph_views.generate_wordcloud_view,
        name="generate_wordcloud_view",
    ),
    path(
        "word-network/", keyword_networkx_views.word_network_view, name="word_network"
    ),
    path("generate_pdf/", generate_pdf_views.generate_pdf, name="generate_pdf"),
]
