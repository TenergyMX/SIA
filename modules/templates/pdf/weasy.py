from pathlib import Path

from django.conf import settings
from django.template.loader import get_template
from django.http import HttpResponse

from weasyprint import HTML, CSS


class WeasyPDF:

    def __init__(self, template, context=None):
        self.template = template
        self.context = context or {}


    def render(self):

        pdf_path = (
            Path(settings.BASE_DIR)
            / "modules"
            / "templates"
            / "pdf"
        )


        self.context.update({

            "header_image":
                (
                    pdf_path /
                    "images" / 
                    "header.png"
                ).as_uri(),


            "footer_image":
                (
                    pdf_path /
                    "images" /
                    "footer.png"
                ).as_uri(),

        })


        template = get_template(
            self.template
        )


        html = template.render(
            self.context
        )


        document = HTML(
            string=html,
            base_url=str(pdf_path)
        ).render(
            stylesheets=[
                CSS(
                    filename=str(
                        pdf_path /
                        "css" /
                        "pdf.css"
                    )
                )
            ]
        )

        pdf = document.write_pdf()

        response = HttpResponse(
            pdf,
            content_type="application/pdf"
        )


        response["Content-Disposition"] = (
            'inline; filename="responsiva.pdf"'
        )


        return response