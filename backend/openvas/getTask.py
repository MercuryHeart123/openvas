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
    
    def get_formatted_date(self, day):
        current_date = datetime.date.today()
        daypass = current_date - datetime.timedelta(days=day)
        formatted_daypass = daypass.strftime("%Y-%m-%d")
        return formatted_daypass
        
    def get_update(self, token):
        self.logger.info('get update with token: ' + token)
        root = Element('envelope')
        child = SubElement(root, "version")

        child.text = "22.06.0"
        nvts = SubElement(root, "nvts")
        cves = SubElement(root, "cves")
        cpes = SubElement(root, "cpes")
        # for i in range(6, -1, -1):
            # text = f"modified>{self.get_formatted_date(i)} and modified<{self.get_formatted_date(i-1)}"
        text = "modified>2023-09-08 and modified<2023-09-09"
        nvt = SubElement(nvts, "nvt")
        resultnvts = self.gmps[token].get_nvts(filter_string=text)
        xmlnvts = ET.fromstring(resultnvts)
        nvt.text = xmlnvts.find("info_count").find("filtered").text
        
        cve = SubElement(cves, "cve")
        resultcves = self.gmps[token].get_cves(filter_string=text)
        xmlcves = ET.fromstring(resultcves)
        cve.text = xmlcves.find("info_count").find("filtered").text
        
        cpe = SubElement(cpes, "cpe")
        resultcpes = self.gmps[token].get_cpes(filter_string=text)
        xmlcpes = ET.fromstring(resultcpes)
        cpe.text = xmlcpes.find("info_count").find("filtered").text
        # result = self.gmps[token].get_version()
        return root
    
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
        
    def healthCheck(self):
        self.logger.info('helth check')

        # if self.gmp == None or self.gmp.is_connected() != True:
        #     self.gmp = None
        #     self.connect()

        # if self.gmp != None and self.gmp.is_authenticated() != True:
        #     self.authen()

    # def authen(self):
    #     if self.gmp != None:
    #         self.gmp.authenticate('admin', 'admin')

    def get_tasks(self):
        tasks = self.gmp.get_tasks(filter_string="rows=100")
        # tasks = self.gmp.get_operating_systems()
        return tasks

    def get_task(self, task_id=None):
        self.healthCheck()
        if task_id is None:
            tasks = self.get_tasks()
            return tasks

        task = self.gmp.get_task(task_id=task_id)
        return task

    def get_scanners(self):
        scanners = self.gmp.get_scanners()
        return scanners

    def get_scanner(self, scanner_id=None):
        self.healthCheck()
        if scanner_id is None:
            scanners = self.get_scanners()
            return scanners

        scanner = self.gmp.get_scanner(scanner_id=scanner_id)
        return scanner

    def create_task(self, name, comment, target_id, config_id, scanner_id):
        self.logger.info(name, comment, target_id, config_id, scanner_id)

        self.healthCheck()
        try:
            task = self.gmp.create_task(
                name=name, comment=comment, target_id=target_id, config_id=config_id, scanner_id=scanner_id)
        except Exception as e:
            self.logger.error(e)
            self.logger.error('create_task failed')
            raise Exception('create_task failed')

        return task

    def create_target(self, name, comment, hosts, port_range):
        self.healthCheck()
        target = self.gmp.create_target(name=name, comment=comment, hosts=[
                                        hosts], port_range=port_range)
        return target

    def get_targets(self):
        self.healthCheck()
        targets = self.gmp.get_targets(filter_string="rows=100")
        return targets

    def get_target(self, target_id=None):
        self.healthCheck()
        if target_id is None:
            targets = self.get_targets()
            return targets

        target = self.gmp.get_target(target_id=target_id)
        return target

    def get_reports(self, reportId=None):
        self.healthCheck()

        if reportId is None:
            reports = self.gmp.get_reports()
            return reports
        else:
            report = self.gmp.get_report(
                report_id=reportId, ignore_pagination=True)
            return report

    def start_task(self, task_id):
        self.healthCheck()
        if task_id is None:
            raise Exception('task_id is None')

        task = self.gmp.start_task(task_id=task_id)
        return task

    def get_nvt(self):
        self.healthCheck()
        nvt = self.gmp.get_nvt(nvt_id="1.3.6.1.4.1.25623.1.0.111038")
        return nvt
