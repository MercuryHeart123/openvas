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

# def loginController(request):
#     try:
#         if request.method == 'POST':
#             decoded_str = request.body.decode()
#             data_dict = parseFormdata(decoded_str)
#             logger.info(data_dict)
            
#             result = 'test'
#             statusCode = 200
#             # if (data_dict.get('taskId') != None):
#             #     result = views.getSingleTask(data_dict.get('taskId'))
#             #     statusCode = 200

#             # else:
#             #     raise ("taskId is required")

#         elif request.method == 'GET':
#             result = views.login()
#             # xmlResult = views.getAllTask()
#             # result = ElementTree.tostring(tree, encoding="utf-8")
#             # result = xmlToJson(xmlResult)
#             # result = result['get_tasks_response']['tas
#             statusCode = 200
#             logger.debug(result)

#         else:
#             raise ("Method not allowed")

#     except Exception as e:
#         result = str(e)
#         logger.error(e)
        
#         statusCode = 500

#     return HttpResponse(result, status=statusCode, content_type='application/xml')

def loginController(request):
    logger.info(request.GET.get('cmd', ''))
    try:
        if request.method == 'POST':
            decoded_str = request.body.decode()
            data_dict = parseFormdata(decoded_str)
            if (data_dict.get('username') != None and data_dict.get('password') != None):
                result = views.login(data_dict.get('username'), data_dict.get('password'))
                statusCode = 200

            else:
                raise ("taskId is required")
        elif request.method == 'GET' and request.GET.get('cmd', '') == 'get_updates':
            logger.info(request.GET.get('token', ''))
            root = Element('envelope')
            child = SubElement(root, "version")

            child.text = "22.06.0"
            nvts = SubElement(root, "nvts")
            cves = SubElement(root, "cves")
            certs = SubElement(root, "certs")
            for i in range(0, 7):
                nvt = SubElement(nvts, "nvt")
                nvt.attrib['oid'] = f"{i}"
                nvt.text = f"{random.randint(0, 100)}"
                cve = SubElement(cves, "cve")
                cve.attrib['oid'] = f"{i}"
                cve.text = f"{random.randint(0, 100)}"
                cert = SubElement(certs, "cert")
                cert.attrib['oid'] = f"{i}"
                cert.text = f"{random.randint(0, 100)}"

            result = tostring(root).decode('utf-8')
            statusCode = 200
        else:
            raise BaseException("Method not allowed")

    except Exception as e:
        result = str(e)
        logger.error(e)
        
        statusCode = 500

    return HttpResponse(result, status=statusCode, content_type='application/xml')

def viewInterface(request):
    return views.viewInterface(request)


def getTaskController(request):
    try:
        if request.method == 'POST':
            decoded_str = request.body.decode()
            data_dict = json.loads(decoded_str)
            if (data_dict.get('taskId') != None):
                result = views.getSingleTask(data_dict.get('taskId'))
                statusCode = 200

            else:
                raise ("taskId is required")

        elif request.method == 'GET':
            xmlResult = views.getAllTask()

            result = xmlToJson(xmlResult)
            # result = result['get_tasks_response']['tas
            statusCode = 200

        else:
            raise ("Method not allowed")

    except Exception as e:
        result = str(e)
        statusCode = 500

    result = result.replace("@", "")
    return HttpResponse(result, status=statusCode, content_type='application/json')


def createTaskController(request):
    try:
        if request.method == 'POST':
            decoded_str = request.body.decode()
            data_dict = json.loads(decoded_str)
            targetId = None
            if ((data_dict.get('ip') != None) and (data_dict.get('scanner_id') != None)):
                print(data_dict.get('ip'), data_dict.get('scanner_id'), 'ussss')
                allTarget = views.getAllTarget()
                allTarget = xmlToJson(allTarget)
                allTarget = allTarget.replace("@", "")
                allTarget_dict = json.loads(allTarget)
                allTarget = allTarget_dict['get_targets_response']['target']
                for target in allTarget:
                    logger.info(target['hosts'])
                    if target['hosts'] == data_dict.get('ip'):
                        targetId = target['id']
                        break
                # logger.info(allTarget)
                if targetId == None:
                    targetId = views.createTarget(
                        data_dict.get('ip'), data_dict.get('ip'), data_dict.get('ip'), "1-65535")
                    targetIdJson = xmlToJson(targetId)
                    targetIdJson = targetIdJson.replace("@", "")
                    targetId_dict = json.loads(targetIdJson)
                    targetId = targetId_dict['create_target_response']['id']
                result = views.createTask(data_dict.get('ip'), data_dict.get(
                    'ip'), targetId, 'daba56c8-73ec-11df-a475-002264764cea', data_dict.get('scanner_id'))
                statusCode = 200
            else:
                raise ("some parameter is missing")

        else:
            raise ("Method not allowed")

    except Exception as e:
        result = str(e)
        statusCode = 500

    # result = result.replace("@", "")
    return HttpResponse(result, status=statusCode, content_type='application/json')


def getTargetController(request):
    try:

        if request.method == 'GET':
            xmlResult = views.getAllTarget()
            result = xmlToJson(xmlResult)
            # result = result['get_tasks_response']['task']
            statusCode = 200

        else:
            raise ("Method not allowed")

    except Exception as e:
        result = str(e)
        statusCode = 500

    result = result.replace("@", "")
    return HttpResponse(result, status=statusCode, content_type='application/json')


def getScannerController(request):
    try:
        if request.method == 'POST':
            decoded_str = request.body.decode()
            data_dict = json.loads(decoded_str)
            if (data_dict.get('scannerId') != None):
                result = views.getSingelScanner(data_dict.get('scannerId'))
                statusCode = 200

            else:
                raise ("taskId is required")

        elif request.method == 'GET':
            xmlResult = views.getAllScanner()
            result = xmlToJson(xmlResult)
            # result = result['get_tasks_response']['task']
            statusCode = 200

        else:
            raise ("Method not allowed")

    except Exception as e:
        result = str(e)
        statusCode = 500

    result = result.replace("@", "")
    return HttpResponse(result, status=statusCode, content_type='application/json')


def createTargetController(request):
    try:
        if request.method == 'POST':
            decoded_str = request.body.decode()
            data_dict = json.loads(decoded_str)
            if (data_dict.get('name') and data_dict.get('comment') and data_dict.get('hosts') and data_dict.get('port_range') != None):
                result = views.createTarget(data_dict.get('name'), data_dict.get('comment'), data_dict.get(
                    'hosts'), data_dict.get('port_range'))
                statusCode = 200

            else:
                raise ("some parameter is missing")

        else:
            raise ("Method not allowed")

    except Exception as e:
        result = str(e)
        statusCode = 500

    result = result.replace("@", "")
    return HttpResponse(result, status=statusCode, content_type='application/json')


def getReportController(request):
    try:
        if request.method == 'POST':
            decoded_str = request.body.decode()
            data_dict = json.loads(decoded_str)
            if (data_dict.get('reportId') != None):
                try:
                    logger.info('1111')

                    xmlResult = views.getSingleReport(
                        data_dict.get('reportId'))
                    statusCode = 200
                    result = xmlToJson(xmlResult)
                    result = result.replace("@", "")
                    result_dict = json.loads(result)
                    # for element in tree.:
                    if result_dict['get_reports_response']['status'] == '404':
                        statusCode = 500
                        raise Exception("Report not found")
                except Exception as e:
                    statusCode = 500
                    raise Exception(e)

            else:
                raise Exception("reportId is required")

        elif request.method == 'GET':
            xmlResult = views.getAllReport()

            # result = result['get_tasks_response']['task']
            statusCode = 200

        else:
            raise Exception("Method not allowed")

    except Exception as e:
        result = str(e)
        return HttpResponse(result, status=500, content_type='application/json')

    return HttpResponse(result, status=statusCode, content_type='application/json')


def startTaskController(request):
    try:
        if request.method == 'POST':
            decoded_str = request.body.decode()
            data_dict = json.loads(decoded_str)
            if (data_dict.get('task_id') != None):
                xmlResult = views.startTask(data_dict.get('task_id'))
                result = xmlToJson(xmlResult)
                statusCode = 200

            else:
                raise Exception("task_id is required")

        else:
            raise Exception("Method not allowed")

    except Exception as e:
        result = str(e)
        statusCode = 500

    result = result.replace("@", "")
    return HttpResponse(result, status=statusCode, content_type='application/json')


def getNvtController(request):
    try:
        if request.method == 'GET':
            xmlResult = views.getNvt()
            result = xmlToJson(xmlResult)
            statusCode = 200

        else:
            raise Exception("Method not allowed")

    except Exception as e:
        result = str(e)
        statusCode = 500

    result = result.replace("@", "")
    return HttpResponse(result, status=statusCode, content_type='application/json')
