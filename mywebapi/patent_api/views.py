from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Count
from django.db import models
from .models import Patent


def index(request):
    return render(request, "index.html")


def search(query):
    if query:
        return Patent.objects.filter(title__icontains=query)
    else:
        return Patent.objects.none()


def patent_list(request):
    query = request.GET.get("q", "")
    patents = search(query)
    return render(request, "results.html", {"patents": patents})


def patent_year_distribution(request):
    query = request.GET.get("q", "")
    patents = search(query)

    # 对专利数据按年份进行分组和计数
    year_distribution = (
        patents.values("year").annotate(count=models.Count("id")).order_by("year")
    )

    # 准备数据用于生成图表
    years = [item["year"] for item in year_distribution]
    counts = [item["count"] for item in year_distribution]

    # 将数据传递到模板
    context = {"years": years, "counts": counts}
    return render(request, "graph.html", context)
