from django.http import HttpResponse, JsonResponse
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from base64 import b64decode
from io import BytesIO
import json

from ..models import UserSearch


def get_report_data(request):
    search_keyword = request.GET.get("searchKeyword")
    user = request.user
    user_search = UserSearch.objects.filter(
        user=user, search_word=search_keyword
    ).first()

    if user_search:
        data = {
            "searchKeyword": search_keyword,
            "charts": [
                {
                    "title": "Distribution Line Chart",
                    "imageData": user_search.distribution_line_base64,
                },
                {
                    "title": "Distribution Bar Chart",
                    "imageData": user_search.distribution_bar_base64,
                    "text": user_search.distribution_conclusion,
                },
                {
                    "title": "Innovation Map Chart",
                    "imageData": user_search.innovation_map_base64,
                },
                {
                    "title": "Innovation Bar Chart",
                    "imageData": user_search.innovation_bar_base64,
                    "text": user_search.innovation_conclusion,
                },
                {
                    "title": "Network",
                    "imageData": user_search.network_base64,
                    "text": user_search.network_conclusion,
                },
                {
                    "title": "Wordcloud",
                    "imageData": user_search.wordcloud_base64,
                },
                {
                    "title": "Word Network",
                    "imageData": user_search.word_network_base64,
                },
            ],
        }
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "No data found"}, status=404)


def generate_pdf(request):
    pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            search_keyword = data.get("searchKeyword", "")
            charts = data.get("charts", [])

            response = HttpResponse(content_type="application/pdf")
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{search_keyword}的分析报告.pdf"'

            buffer = BytesIO()
            p = canvas.Canvas(buffer)

            p.setFont("SimSun", 16)
            p.drawString(200, 800, f"{search_keyword}的分析报告")

            y_position = 780
            image_height = 300

            style = ParagraphStyle(name="Normal", fontName="SimSun", fontSize=12)

            for chart in charts:
                title = chart.get("title", "")
                chart_image = (
                    b64decode(chart["imageData"].split(",")[1])
                    if chart["imageData"]
                    else None
                )
                chart_text = chart.get("text", "")

                if y_position < 100:
                    p.showPage()
                    y_position = 780

                p.setFont("SimSun", 14)
                p.drawString(50, y_position, title)
                y_position -= 10

                if chart_image:
                    chart_image_stream = BytesIO(chart_image)
                    chart_image_stream.seek(0)
                    y_position -= image_height
                    p.drawImage(
                        ImageReader(chart_image_stream),
                        50,
                        y_position,
                        width=450,
                        height=image_height,
                    )

                if chart_text:
                    y_position -= 30
                    para = Paragraph(chart_text, style)
                    para.wrapOn(p, 450, 50)
                    para.drawOn(p, 50, y_position - 20)
                    y_position -= 80

            p.save()
            buffer.seek(0)
            response.write(buffer.getvalue())
            buffer.close()

            return response
        except Exception as e:
            return HttpResponse(f"Error generating PDF: {e}", status=500)

    return HttpResponse("Invalid request", status=400)


# def generate_pdf(request):
#     pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             text = data.get("text", "")

#             response = HttpResponse(content_type="application/pdf")
#             response["Content-Disposition"] = 'attachment; filename="report.pdf"'

#             buffer = BytesIO()
#             p = canvas.Canvas(buffer)

#             image_height = 300
#             y_position = 750

#             for chart in data.get("charts", []):
#                 title = chart.get("title", "")
#                 chart_image = b64decode(chart["imageData"].split(",")[1])
#                 chart_image_stream = BytesIO(chart_image)
#                 chart_image_stream.seek(0)

#                 if y_position < 300:
#                     p.showPage()
#                     y_position = 750

#                 p.setFont("SimSun", 12)
#                 p.drawString(50, y_position, title)
#                 y_position -= 20

#                 y_position -= image_height

#                 p.drawImage(
#                     ImageReader(chart_image_stream),
#                     50,
#                     y_position,
#                     width=400,
#                     height=image_height,
#                 )

#             p.showPage()
#             p.setFont("SimSun", 14)
#             y_position = 750
#             p.drawString(50, y_position, "结论")
#             y_position -= 20
#             p.setFont("SimSun", 12)
#             p.drawString(50, y_position, text)
#             p.save()
#             buffer.seek(0)
#             response.write(buffer.getvalue())
#             buffer.close()

#             return response
#         except Exception as e:
#             return HttpResponse(f"Error generating PDF: {e}", status=500)

#     return HttpResponse("Invalid request", status=400)
