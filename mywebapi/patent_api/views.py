import base64
from collections import defaultdict
import csv
import json
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Count
from django.db import models
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from base64 import b64decode
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


def patent_year_distribution(request):
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


# def generate_pdf(request):
#     response = HttpResponse(content_type="application/pdf")
#     response["Content-Disposition"] = 'attachment; filename="test.pdf"'

#     buffer = BytesIO()
#     p = canvas.Canvas(buffer)

#     # 使用已知良好的 base64 图像数据
#     known_good_image_data = "data:image/png;base64,..."  # 替换为实际的 base64 数据
#     image_data = b64decode(known_good_image_data.split(",")[1])
#     image_stream = BytesIO(image_data)
#     p.drawImage(ImageReader(image_stream), 100, 500, width=400, height=300)

#     p.showPage()
#     p.save()
#     buffer.seek(0)
#     response.write(buffer.getvalue())
#     return response
