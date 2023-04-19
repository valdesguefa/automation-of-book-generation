from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa

from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.views import APIView
import os
import pdfkit
from BookAI import settings

from django.http import FileResponse

# Create your views here.

def render_to_pdf(template_src, context_dict = {}) :
    template = get_template(template_src)
    html = template.render(context_dict)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err :
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    return None

class ViewPDF(APIView) :
    #@transaction.atomic
    @csrf_exempt
    def post(self, request, *args, **kwargs) :
        data2 = request.data
        print(data2)
        pdf = render_to_pdf('app/report.html', data2)
        return HttpResponse(pdf, content_type = 'application/pdf')


class DownloadPDF(APIView) :
    @csrf_exempt
    def post(self, request, *args, **kwargs) :
        data = request.data
        print(data)
        # pdf = render_to_pdf('app/report.html', data)
        # print('define response')
        # reponse = HttpResponse(pdf, content_type = 'application/pdf')
        # filename = "sample_%s.pdf"%("12345678")
        # content = "attachment; filename='%s'"%(filename)
        # reponse['content-Disposition'] = content

        #Define path to wkhtmltopdf.exe
        path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

        #Define url
        template = get_template('app/wonderbly.html')
        
        html = template.render(data)
        
        file_name = 'invoice.pdf'
        pdf_path = "wonderbly.pdf"
        # options1 = {
        #     'page-size': 'A4',
        #     'disable-smart-shrinking': '',
        #     "enable-local-file-access": "",
        #     'margin-top': '0in',
        #     'margin-right': '0in',
        #     'margin-bottom': '0in',
        #     'margin-left': '0in',
        #     'encoding': "UTF-8",
        #     "load-error-handling": "ignore"
            
        # }
        options = {
    'page-size': 'A4',
    'disable-smart-shrinking': '',
    "enable-local-file-access": "",
    'margin-top': '0in',
    'margin-right': '0in',
    'margin-bottom': '0in',
    'margin-left': '0in',
    'encoding': "UTF-8",
    
}
        print(html)
        pdfkit.from_string(html, pdf_path, options=options)
        return FileResponse(open(pdf_path, 'rb'), filename=file_name, content_type='application/pdf')

def index(request) :
    context = {}
    return render(request, 'app/index.html', context)