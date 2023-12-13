from django.http import HttpResponse
from django.shortcuts import render
from .models import Patent


def index(request):
    return render(request, "index.html")


def search(request):
    query = request.GET.get("q", "")  # 获取搜索词
    if query:
        patents = Patent.objects.filter(title__icontains=query)  # 在标题中搜索
    else:
        patents = Patent.objects.none()  # 如果没有查询词，则不返回任何结果

    return render(request, "results.html", {"patents": patents})
