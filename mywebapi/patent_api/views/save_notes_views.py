from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import UserSearch
import json


@csrf_exempt
@require_POST
def save_notes(request):
    data = json.loads(request.body)
    content = data.get("content")
    search_keyword = data.get("searchKeyword")
    analysis_type = data.get("analysisType")
    user = request.user

    # 根据用户和搜索关键词找到对应的 UserSearch 对象
    user_search, created = UserSearch.objects.get_or_create(
        user=user, search_word=search_keyword
    )

    if analysis_type == "distribution":
        user_search.distribution_conclusion = content
    elif analysis_type == "innovation":
        user_search.innovation_conclusion = content
    elif analysis_type == "network":
        user_search.network_conclusion = content
    user_search.save()

    return JsonResponse({"status": "success"})
