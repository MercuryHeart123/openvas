from django.apps import apps
from utils.xmlUtil import xmlToJson
import logging
from xml.etree import cElementTree as ET
from xml.etree import ElementTree
logger = logging.getLogger(__name__)

gvm_service = apps.get_app_config('myapp').gvm_service

def login(username, password):
    response = gvm_service.login(username, password)
    return response

def getUpdate(token):
    if(token == None and gvm_service.checkToken(token) == False):
        return None
    response = gvm_service.get_update(token)
    return response

def getReports(reportId, token):
    response = gvm_service.get_reports(reportId, token)
    return response

def getTarget(targetId, token):
    response = gvm_service.get_target(targetId, token)
    return response

def getTaskName(report):
    name = report.find('./report/report/task/name').text
    
    return name

def getTargetId(report):
    target_id = report.find('./report/report/task/target').get('id')
    return target_id

def getHostResult(report,targetHost):
    all_host_result = {}
    if int(report.find('./report/report/hosts/count').text) == 1:
        all_host_result[targetHost] = {
            'High': report.find('./report/report/result_count/hole/filtered').text,
            'Medium': report.find('./report/report/result_count/warning/filtered').text,
            'Low': report.find('./report/report/result_count/info/filtered').text,
            'severity': report.find('./report/report/severity/filtered').text
        }
        return all_host_result
        
    all_host = report.findall('./report/report/host/ip')
    
    for host in all_host:
        all_host_result[f'{host.text}'] = {
            'High': 0,
            'Medium': 0,
            'Low': 0,
            'severity': 0
        }
        
    host_results = report.findall('./report/report/results/result')
    for host_result in host_results:
        host = host_result.find('./host').text
        all_host_result[host][f'{host_result.find("./threat").text}'] += 1
        if float(all_host_result[host]['severity']) < float(host_result.find('./severity').text):
            all_host_result[host]['severity'] = host_result.find('./severity').text

    return all_host_result

def getData(taskId, token):
    if(token == None and gvm_service.checkToken(token) == False):
        return None
    report  = getReports(taskId, token)
    
    reportXml = ET.fromstring(report)
    
    if reportXml.get('status') == '200':
        name = getTaskName(reportXml)
        target_Id = getTargetId(reportXml)
        targetXml = ET.fromstring(getTarget(target_Id, token))
        targetHost = targetXml.find('./target/hosts').text
        allHostResult = getHostResult(reportXml,targetHost)
        
        obj = {'name': name, 'targetHost': targetHost, 'allHostResult': allHostResult}
        return obj
    return None