from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
# def all_user(request):
#     return HttpResponse("Returing")


from django.http import JsonResponse
from .models import Patent  # 导入你的模型


def all_user(request):
    data = Patent.objects.all()  # 从数据库获取数据
    data_list = list(data.values())  # 将查询集转换为字典列表
    return JsonResponse(data_list, safe=False)  # 返回 JSON 响应
