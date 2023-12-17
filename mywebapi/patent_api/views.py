from collections import defaultdict
from django.conf import settings
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
    return render(request, "distribution.html", context)


def province_innovation(request):
    query = request.GET.get("q", "")
    patents = search(query)

    province_counts = (
        patents.values("province").annotate(count=Count("id")).order_by("-count")
    )
    print(province_counts)

    provinces = [item["province"] for item in province_counts]
    province_count = [item["count"] for item in province_counts]

    context = {
        "provinces": provinces,
        "province_count": province_count,
        "baidu_map_ak": settings.BAIDU_MAP_AK,
    }
    return render(request, "innovation.html", context)


def network_view(request):
    query = request.GET.get("q", "")
    patents = search(query)

    # 提取网络数据
    nodes = set()
    links = defaultdict(int)

    for patent in patents:
        entities = patent.apos.split(";")
        for entity in entities:
            nodes.add(entity)
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                links[(entities[i], entities[j])] += 1

    nodes_data = [{"name": node} for node in nodes]
    links_data = [
        {"source": source, "target": target, "value": links[(source, target)]}
        for source, target in links
    ]

    # 将数据传递到模板
    return render(
        request,
        "network.html",
        {
            "nodes_data": nodes_data,
            "links_data": links_data,
        },
    )
