from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import UserSearch
import json


@csrf_exempt
@require_POST
def save_chart_data(request):
    try:
        data = json.loads(request.body)
        chart_id = data["chartId"]
        base64_data = data["base64Data"]
        search_keyword = data["searchKeyword"]
        user = request.user

        user_search, _ = UserSearch.objects.get_or_create(
            user=user, search_word=search_keyword
        )

        # 根据 chart_id 选择对应的字段
        if chart_id == "distributionLineChart":
            user_search.distribution_line_base64 = base64_data
        elif chart_id == "distributionBarChart":
            user_search.distribution_bar_base64 = base64_data
        elif chart_id == "innovationBarChart":
            user_search.innovation_bar_base64 = base64_data
        elif chart_id == "innovationMapChart":
            user_search.innovation_map_base64 = base64_data
        elif chart_id == "networkChart":
            user_search.network_base64 = base64_data

        user_search.save()

        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
