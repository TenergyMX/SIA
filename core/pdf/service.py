from io import BytesIO

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML


class PDFService:

    @staticmethod
    def render(request, template_name, context, filename="documento.pdf"):
        html = render_to_string(
            template_name,
            context,
            request=request
        )

        pdf = HTML(
            string=html,
            base_url=request.build_absolute_uri("/")
        )

        pdf_buffer = BytesIO()
        pdf.write_pdf(pdf_buffer)

        response = HttpResponse(
            pdf_buffer.getvalue(),
            content_type="application/pdf"
        )

        response["Content-Disposition"] = f'inline; filename="{filename}"'

        return response