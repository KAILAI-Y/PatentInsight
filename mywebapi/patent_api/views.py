import os
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Count
from django.db import models
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from collections import Counter, defaultdict
from io import BytesIO
import base64
from base64 import b64decode
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
import jieba.analyse
import jieba.posseg as pseg
import csv
import json
from openai import OpenAI
from .models import Patent

client = OpenAI(api_key=settings.OPENAI_API_KEY)


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

    paginator = Paginator(patents, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "result.html",
        {
            "page_obj": page_obj,
            "total_count": paginator.count,
        },
    )


def download_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="patents.csv"'
    response.write("\ufeff".encode("utf8"))

    writer = csv.writer(response)
    writer.writerow(["Title", "Year", "Abstract"])

    query = request.GET.get("q", "")
    patents = search(query)

    for patent in patents:
        writer.writerow([patent.title, patent.year, patent.abstract])

    return response


def year_distribution(request):
    query = request.GET.get("q", "")
    patents = search(query)

    year_distribution = (
        patents.values("year").annotate(count=models.Count("id")).order_by("year")
    )

    years = [item["year"] for item in year_distribution]
    counts = [item["count"] for item in year_distribution]

    most_patents_year = max(year_distribution, key=lambda x: x["count"])["year"]
    least_patents_year = min(year_distribution, key=lambda x: x["count"])["year"]

    context = {
        "years": years,
        "counts": counts,
        "most_patents_year": most_patents_year,
        "least_patents_year": least_patents_year,
    }
    return render(request, "distribution.html", context)


def province_innovation(request):
    query = request.GET.get("q", "")
    patents = search(query)

    province_counts = (
        patents.values("province").annotate(count=Count("id")).order_by("-count")[:10]
    )
    print(province_counts)

    provinces = [item["province"] for item in province_counts]
    province_count = [item["count"] for item in province_counts]

    context = {
        "provinces": provinces,
        "province_count": province_count,
        # "baidu_map_ak": settings.BAIDU_MAP_AK,
    }
    return render(request, "innovation.html", context)


def network_view(request):
    query = request.GET.get("q", "")
    patents = search(query)

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

    return render(
        request,
        "network.html",
        {
            "nodes_data": nodes_data,
            "links_data": links_data,
        },
    )


def generate_pdf(request):
    pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get("text", "")

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="report.pdf"'

            buffer = BytesIO()
            p = canvas.Canvas(buffer)

            image_height = 300
            y_position = 750

            for chart in data.get("charts", []):
                title = chart.get("title", "")
                chart_image = b64decode(chart["imageData"].split(",")[1])
                chart_image_stream = BytesIO(chart_image)
                chart_image_stream.seek(0)

                if y_position < 300:
                    p.showPage()
                    y_position = 750

                p.setFont("SimSun", 12)
                p.drawString(50, y_position, title)
                y_position -= 20

                y_position -= image_height

                p.drawImage(
                    ImageReader(chart_image_stream),
                    50,
                    y_position,
                    width=400,
                    height=image_height,
                )

            p.showPage()
            p.setFont("SimSun", 14)
            y_position = 750
            p.drawString(50, y_position, "结论")
            y_position -= 20
            p.setFont("SimSun", 12)
            p.drawString(50, y_position, text)
            p.save()
            buffer.seek(0)
            response.write(buffer.getvalue())
            buffer.close()

            return response
        except Exception as e:
            return HttpResponse(f"Error generating PDF: {e}", status=500)

    return HttpResponse("Invalid request", status=400)


@csrf_exempt
@require_http_methods(["POST"])
def gpt_request(request):
    try:
        # 解析请求体中的数据
        data = json.loads(request.body)
        base64_images = data.get("base64_images", [])
        text = data.get("text")

        # 构建用于 GPT-4 视觉模型的消息
        messages = [{"type": "text", "text": text}]
        messages.extend(
            [
                {"type": "image_url", "image_url": {"url": base64_image}}
                for base64_image in base64_images
            ]
        )

        # 调用 OpenAI GPT-4 视觉模型
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": messages,
                }
            ],
            max_tokens=300,
        )

        # 提取并返回响应数据
        generated_text = response.choices[0].message.content
        last_period_index = generated_text.rfind("。")
        if last_period_index != -1:
            generated_text = generated_text[: last_period_index + 1]
        return JsonResponse({"response": generated_text})

    except json.JSONDecodeError as e:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def generate_wordcloud(patents, query, stopwords_path):
    combined_text = " ".join(patent.title + " " + patent.abstract for patent in patents)

    # 设置结巴分词的停用词
    jieba.analyse.set_stop_words(stopwords_path)
    words = pseg.cut(combined_text)

    # 提取名词
    nouns = [word for word, flag in words if flag.startswith("n")]

    # 将名词合并为一个长字符串
    combined_nouns = " ".join(nouns)

    # 提取关键词和权重
    top_keywords = jieba.analyse.textrank(combined_nouns, topK=20, withWeight=True)
    word_frequencies = {word: weight for word, weight in top_keywords}

    font_path = os.path.join(
        settings.BASE_DIR, "patent_api", "static", "font", "SimSun.ttf"
    )

    # 创建词云对象
    wc = WordCloud(
        font_path=font_path,
        width=800,
        height=400,
        background_color="white",
    )

    # 根据词频生成词云
    wc.generate_from_frequencies(word_frequencies)

    # 将词云图像转换为 Base64 编码
    img = wc.to_image()
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64


def generate_wordcloud_view(request):
    query = request.GET.get("q", "")
    patents = search(query)

    stopwords_path = os.path.join(
        settings.BASE_DIR, "patent_api", "static", "baidu_stopwords.txt"
    )

    if patents.exists():
        # 获取 Base64 编码的词云图像
        wordcloud_image_base64 = generate_wordcloud(patents, query, stopwords_path)
    else:
        wordcloud_image_base64 = None

    return render(
        request, "wordcloud.html", {"wordcloud_image_base64": wordcloud_image_base64}
    )
