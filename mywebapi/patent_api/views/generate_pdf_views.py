from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from base64 import b64decode
from io import BytesIO
import json


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
