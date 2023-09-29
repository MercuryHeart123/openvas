from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform
from xml.etree.ElementTree import Element, SubElement, tostring
import logging
import uuid
from xml.etree import cElementTree as ET
import random
import datetime

class GvmService:
    def __init__(self, path='/run/gvmd/gvmd.sock'):
        self.path = path
        self.connection = UnixSocketConnection(path=self.path)
        self.transform = EtreeTransform()
        self.gmp = None
        self.gmps = {}
        self.logger = logging.getLogger(__name__)

    def login(self, username, password):
        genUid = str(uuid.uuid4())
        result = self.authen(username, password, genUid)
        rootxml = ET.fromstring(result)
        if rootxml.get('status') == '200':
            root = Element('envelope')
            child = SubElement(root, "version")
            role = SubElement(root, "role")
            token = SubElement(root, "token")
            child.text = "22.06.0"
            token.text = genUid
            role.text = rootxml.find('role').text
            return tostring(root).decode('utf-8')
        else:
            return result
    
    def logout(self, token):
        self.logger.info('try to logout with token: ' + token)
        if self.checkToken(token) == True:
            self.gmps[token] = None
            return 'success'
        else:
            return 'failed'
        
    def connect(self, genUid):
        self.logger.info('try to connecting gvmd with genUid: ' + genUid)
        # if self.gmp[genUid] != None and self.gmp[genUid].is_connected() == True:
        #     self.connection.disconnect()
        try:
            with Gmp(connection=self.connection) as gmp:
                self.gmps[genUid] = gmp

        except Exception as e:
            self.logger.error('connect to gvmd failed')
            self.logger.error(e)
            self.gmps[genUid] = None

    def checkToken(self, token):
        self.logger.info('check token: ' + token)
        for key in self.gmps.keys():
            if key == token:
                return True
        return False


    def authen(self, username, password, genUid):
        try:
            self.logger.info('authening to gvmd') 
            self.connect(genUid)
            result = self.gmps[genUid].authenticate(username, password)
            
        except Exception as e:  
            self.logger.error('authen to gvmd failed')
            self.logger.error(e)
            self.gmps[genUid] = None
            result = None
        return result


    def get_reports(self, reportId=None, token=None, filter="apply_overrides=0 levels=hml rows=100 min_qod=70 first=1 sort-reverse=severity"):
        if reportId is None:
            reports = self.gmps[token].get_reports()
            return reports
        else:
            report_format = self.get_report_formats(token)
            report = self.gmps[token].get_report(
                report_id=reportId, report_format_id=report_format, filter_string=filter)
            return report

    def get_report_formats(self, token):
        report_formats = self.gmps[token].get_report_formats()
        rootxml = ET.fromstring(report_formats)
        if rootxml.get('status') == '200':
            for element in rootxml.iter():
                if element.tag == 'report_format':
                    formatId = element.get('id')
                    if element.find('name').text == 'XML':

                        return formatId
        return None

    def get_target(self, targetId ,token):
        targets = self.gmps[token].get_target(targetId)
        return targets
