from . import views
from django.http import JsonResponse
from django.http import HttpResponse
import openvas.getTask as openvas
from utils.xmlUtil import xmlToJson
import json
from xml.etree.ElementTree import Element, SubElement, tostring
import logging
import random


logger = logging.getLogger(__name__)

def parseFormdata(raw_form_data):
    boundary = raw_form_data.split('------WebKitFormBoundary')
    parts = boundary[1:-1]  # Remove the first and last empty parts
    
    # Initialize a dictionary to store form fields and their values
    form_data_dict = {}

    # Iterate through the parts and extract the field names and values
    for part in parts:
        if 'Content-Disposition: form-data; name="' in part:
            # Extract the field name
            field_name = part.split('name="')[1].split('"')[0]
            
            # Extract the field value (remove leading and trailing whitespace)
            field_value = part.split('\n')[3].strip()
            
            # Store the field name and value in the dictionary
            form_data_dict[field_name] = field_value
    return form_data_dict

def dowloadReportController(request):
    decoded_str = request.body.decode()
    data_dict = json.loads(decoded_str)
    try :
        if data_dict.get('reportIdArray') != None : 
            obj = views.getData(reportIdArray= data_dict.get('reportIdArray'), token= data_dict.get('token'))
            if len(data_dict.get('reportIdArray')) > 1 :
                response = HttpResponse(views.getPdf(obj, True),status=200, content_type='application/pdf')
            else:
                response = HttpResponse(views.getPdf(obj),status=200, content_type='application/pdf')
            response['Content-Disposition'] = "attachment; filename=myfilename.pdf"
        else :
            raise Exception("reportIdArray is required")
        
    except Exception as e:
        response = HttpResponse(str(e), status=500)

    return response
    
def loginController(request):
    try:
        if request.method == 'POST':
            decoded_str = request.body.decode()
            data_dict = parseFormdata(decoded_str)
            if (data_dict.get('username') != None and data_dict.get('password') != None):
                result = views.login(data_dict.get('username'), data_dict.get('password'))
                statusCode = 200
            else:
                raise BaseException("username and password is required")
        else:
            raise BaseException("Method not allowed")

    except Exception as e:
        result = str(e)
        logger.error(e)
        statusCode = 500

    return HttpResponse(result, status=statusCode, content_type='application/xml')

def logoutController(request):
    decoded_str = request.body.decode()
    data_dict = json.loads(decoded_str)
    try:
        if request.method == 'POST':
            djangoToken = data_dict.get('djangotoken')
            if (djangoToken != None):
                result = views.logout(djangoToken)
                statusCode = 200

            else:
                raise BaseException("djangotoken is required")

        else:
            raise BaseException("Method not allowed")
    except Exception as e:
        result = str(e)
        logger.error(e)
        
        statusCode = 500
        
    return HttpResponse({"result":result}, status=statusCode, content_type='application/json')