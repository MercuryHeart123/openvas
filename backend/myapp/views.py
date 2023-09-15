from django.apps import apps
from utils.xmlUtil import xmlToJson
import logging

gvm_service = apps.get_app_config('myapp').gvm_service

def login(username, password):
    response = gvm_service.login(username, password)
    return response

def getUpdate(token):
    if(token == None and gvm_service.checkToken(token) == False):
        return None
    response = gvm_service.get_update(token)
    return response

def getSingleTask(taskId):
    response = gvm_service.get_task(taskId)
    # print(response)
    return response


def getAllTask():
    response = gvm_service.get_task()
    return response


def getSingelScanner(scannerId):
    response = gvm_service.get_scanner(scannerId)
    return response


def getAllScanner():
    response = gvm_service.get_scanner()
    return response


def createTask(name, comment, targetId, configId, scannerId):
    print(name, comment, targetId, configId, scannerId)
    response = gvm_service.create_task(
        name, comment, targetId, configId, scannerId)
    return response


def createTarget(name, comment, hosts, port_range):
    response = gvm_service.create_target(name, comment, hosts, port_range)
    return response


def getSingleTarget(targetId):
    response = gvm_service.get_target(targetId)
    return response


def getAllTarget():
    response = gvm_service.get_target()
    return response


def getSingleReport(reportId):
    logger = logging.getLogger(__name__)
    logger.info('2131414')

    response = gvm_service.get_reports(reportId)
    return response


def getAllReport():
    response = gvm_service.get_reports()
    return response


def startTask(task_id):
    response = gvm_service.start_task(task_id)
    return response
def getNvt():
    response = gvm_service.get_nvt()
    return response