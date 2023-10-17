from django.apps import apps
from utils.xmlUtil import xmlToJson
import logging
from xml.etree import cElementTree as ET
from xml.etree import ElementTree
from fpdf import FPDF, HTMLMixin
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


import io
from datetime import datetime, timedelta
import numpy as np


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
def getDeltaReport(reportId,reportIdDelta ,token):
    response = gvm_service.get_delta(reportId, reportIdDelta,token)
    return response
def getTaskName(report):
    name = report.find('./report/report/task/name').text
    
    return name

def getTargetId(report):
    target_id = report.find('./report/report/task/target').get('id')
    return target_id
def logout(token):
    response = gvm_service.logout(token)
    return response

def getHostResult(report, targetHost= None):
    all_host_result = {"summary": {"Critical": 0,"High": 0, "Medium": 0, "Low": 0, "severity": 0}}
    if int(report.find('./report/report/hosts/count').text) == 1:
        all_host_result[targetHost] = {
            'Critical': 0,
            'High': 0,
            'Medium': 0,
            'Low': 0,
            'severity': 0
        }
        for severity in report.findall('./report/report/results/result/severity'):
            severityText = getSeverityThreshold(severity.text)
            all_host_result[targetHost][severityText] += 1
            all_host_result['summary'][severityText] += 1
            if float(all_host_result['summary']["severity"]) < float(severity.text):
                    all_host_result['summary']["severity"] = severity.text
            if float(all_host_result[targetHost]['severity']) < float(severity.text):
                    all_host_result[targetHost]['severity'] = severity.text
        # high = report.find('./report/report/result_count/hole/filtered').text
        # medium = report.find('./report/report/result_count/warning/filtered').text
        # low = report.find('./report/report/result_count/info/filtered').text
        # severity = report.find('./report/report/severity/filtered').text
        # all_host_result[targetHost] = {
        #     'High': high,
        #     'Medium': medium,
        #     'Low': low,
        #     'severity': severity
        # }
        # all_host_result["summary"] = {
        #     'High': high,
        #     'Medium': medium,
        #     'Low': low,
        #     'severity': severity
        # }

        return all_host_result
    
    all_host = report.findall('./report/report/host/ip')
    
    for host in all_host:
        all_host_result[f'{host.text}'] = {
            'Critical': 0,
            'High': 0,
            'Medium': 0,
            'Low': 0,
            'severity': 0
        }
        
    host_results = report.findall('./report/report/results/result')
    for host_result in host_results:
        host = host_result.find('./host').text
        severityText = getSeverityThreshold(host_result.find('./severity').text)
        all_host_result[host][severityText] += 1
        all_host_result['summary'][severityText] += 1
        # find max severity
        if float(all_host_result['summary']["severity"]) < float(host_result.find('./severity').text):
            all_host_result['summary']["severity"] = host_result.find('./severity').text
        
        # find max severity of each host
        if float(all_host_result[host]['severity']) < float(host_result.find('./severity').text):
            all_host_result[host]['severity'] = host_result.find('./severity').text
    return all_host_result

def getAllResult(report, allHostResult, targetHost=None):
    results = report.findall('./report/report/results/result')
    
    
    
    for result in results:
        host = None
        if len(results) == 1:
            host = targetHost
        else:  
            host = result.find('./host').text
        if allHostResult[host].get("results") == None:
            allHostResult[host]["results"] = []

        
        tags = result.find('./nvt/tags').text
        parts = tags.split("|")
        for part in parts:
            if part.startswith("summary="):
                desired_text = part[len("summary="):]
                break
        allHostResult[host]["results"].append({
            "name" : result.find('./name').text,
            "severity" : result.find('./severity').text,
            "summary" : desired_text,
            "solution" : result.find('./nvt/solution').text,
            "created" : result.find('./creation_time').text,
        })
        
    # mostScore = data[0]
    # tags = mostScore.find('./nvt/tags').text
    # parts = tags.split("|")
    # for part in parts:
    #     if part.startswith("summary="):
    #         desired_text = part[len("summary="):]
    #         break
    # data_dict = {
    #     "name" : mostScore.find('./name').text,
    #     "host" : mostScore.find('./host').text,
    #     "severity" : mostScore.find('./severity').text,
    #     "summary" : desired_text,
    #     "solution" : mostScore.find('./nvt/solution').text,
    #     "created" : mostScore.find('./creation_time').text,
    # }
    return allHostResult

def getFamily(report):
    allResult = report.findall('./report/report/results/result')
    allFamily = report.findall('./report/report/results/result/nvt/family')
    familysName = {}
    count = {}
    for family in allFamily:
        if family.text not in familysName:
            familysName[family.text] = 1
            
        familysName[family.text] += 1
    sortedFamily = sorted(familysName.items(), key=lambda x: x[1])
    familysName = [item[0] for item in sortedFamily]
    
    
    for result in allResult:
        severity = result.find('./severity').text
        if count.get(getSeverityThreshold(severity)) == None:
            count[getSeverityThreshold(severity)] = [0 for _ in range(len(familysName))]
    
    for result in allResult:
        severity = result.find('./severity').text
        count[getSeverityThreshold(severity)][familysName.index(result.find('./nvt/family').text)] += 1
            # count[getSeverityThreshold(severity)] = [0 for _ in range(5)]
    # index = 0
    # tmp = []
    # for family in familysName:
    #     tmp.append(family + " (" + str(count[index]) + ")")
    #     index += 1
        
        
    return {"familysName":familysName, "count":count}

def getDeltaResult(report,token):
    firstReport = report[0]
    secondReport = report[1]
    deltaReport = getDeltaReport(secondReport, firstReport,token)
    deltaReportXml = ET.fromstring(deltaReport)
    allResult = deltaReportXml.findall('./report/report/results/result')
    for result in allResult:
        host = result.find('./host').text
        delta = result.find('./delta').text
        severity = result.find('./severity').text
        name = result.find('./name').text
        solution = result.find('./nvt/solution').text
        tags = result.find('./nvt/tags').text
        parts = tags.split("|")
        for part in parts:
            if part.startswith("summary="):
                summaryText = part[len("summary="):]
                break
    pass
    
def getData(token = None, reportIdArray = None):
    try :
        if(token == None and gvm_service.checkToken(token) == False):
            raise RuntimeError('token is required')
        if len(reportIdArray) > 1:
            allDataReport = {}
            targetHost = None
            for reportId in reportIdArray:
                report = getReports(reportId, token)
                reportXml = ET.fromstring(report)
                if targetHost == None:
                    target_Id = getTargetId(reportXml)
                    targetXml = ET.fromstring(getTarget(target_Id, token))
                    targetHost = targetXml.find('./target/hosts').text
                if reportXml.get('status') != '200':
                    raise RuntimeError('report not found')
                
                allDataReport[reportId] = reportXml
            
            name = getTaskName(allDataReport[reportIdArray[0]])
            
            # format_string = "%Y-%m-%dT%H:%M:%SZ"
            
            severityPerReport = {}
            for report in allDataReport.keys():
                modficationTime = allDataReport[report].find('./report/modification_time').text
                
                severityPerReport[report] = {
                    "result" : getHostResult(allDataReport[report], targetHost)["summary"],
                    "modification_time" : modficationTime
                }
                # if datetime.strptime(modficationTime, format_string) < datetime.strptime(allDataReport[report].find('./report/modification_time').text, format_string):
                #     modficationTime = allDataReport[report].find('./report/modification_time').text
                #     severityPerReport[report] = {
                #         "result" : getHostResult(allDataReport[report])["summary"],
                #         "modifcationTime" : modficationTime
                #     }
                #     mainReport = allDataReport[report]
            
            keys = list(allDataReport.keys())
            deltaReport = [
                keys[0],
                keys[1]
            ]
            deltaResult = getDeltaResult(deltaReport,token)  
            return {"name": name, "severityPerReport": severityPerReport, 'targetHost': targetHost}
        
        else:
            report  = getReports(reportIdArray[0], token)
            logger.info(report)
            reportXml = ET.fromstring(report)
            name = getTaskName(reportXml)
            target_Id = getTargetId(reportXml)
            targetXml = ET.fromstring(getTarget(target_Id, token))
            targetHost = targetXml.find('./target/hosts').text
            allHostResult = getHostResult(reportXml, targetHost=targetHost)
            
            allResult = getAllResult(reportXml, allHostResult, targetHost=targetHost)
            familys = getFamily(reportXml)
            
            obj = {'name': name, 'targetHost': targetHost, 'allHostResult': allResult, 'familys':familys}
            return obj
    except Exception as e:
        logger.error(e)
        raise RuntimeError(e)
def getSeverityThreshold(severity):
        fSeverity = float(severity)
        if fSeverity >= 9.0:
            return "Critical"
        elif fSeverity >= 7.0:
            return "High"
        elif fSeverity >= 4.0:
            return "Medium"
        else:
            return "Low"
        
def getPdf(data, isDeltaReport = False):
    class PDF(FPDF, HTMLMixin):
        def header(self):
            self.set_font('Arial', 'B', 14)
            self.image('slogo.png', 10, 8, 13, link=self.add_link(page=1))
            self.set_x(25)
            self.cell(self.get_string_width("Terabyte vulnerability"), 5, "Terabyte vulnerability",ln=1)
            self.set_x(25)
            self.cell(self.get_string_width("Assessment report"), 5, "Assessment report",ln=1)
            self.set_draw_color(0,0,0)
            self.cell(0,5, border="B",ln=1)
            
        def footer(self):
            self.set_y(-20)
            self.set_draw_color(0,0,0)
            self.cell(0, 10, border="T",ln=1)
            self.set_font('Arial', 'I', 5)
            self.cell(0, 10, "Disclaimer: This report was automatically generated by a security scanning tool. The results may contain false positives or inaccuracies. It is recommended to conduct manual verification and validation of the findings.", 0, 0)
        
        def createBox(self, allSeverity):
            keyAllSeverity = list(allSeverity.keys())
            maxBoxLength = 0
            for key in keyAllSeverity:
                if key == "severity":
                    continue
                boxLength = self.get_string_width(str(allSeverity[key])) + 8
                maxBoxLength = max(maxBoxLength, boxLength)
                
                
            totalPad = (self.w - ((maxBoxLength + 30) * (len(keyAllSeverity)-1)) + 25) /2
            
            yLevel = self.get_y()
            for key in keyAllSeverity:
                if key == "severity":
                    continue
                self.set_fill_color(getFillColor(threshold=key))
                self.set_text_color(255, 255, 255)
                self.set_font('Arial', 'B', 13)
                self.set_xy(totalPad, yLevel)
                self.cell(maxBoxLength, maxBoxLength, f"{allSeverity[key]}", ln=1, align="C", fill=1)
                strLength = self.get_string_width(str(allSeverity[key]))
                issuseLength = self.get_string_width("Issues")
                strLevel = yLevel + maxBoxLength + 2
                if strLength > maxBoxLength:
                    self.set_xy(totalPad - ((strLength - maxBoxLength) / 2), strLevel)
                    self.set_text_color(119,121,123)
                    self.cell(strLength, 7, key, ln=1, align="C")
            # pdf.cell(pdf.get_string_width("Medium"), 7, "Medium", ln=1)
            # pdf.set_font('Arial', '', 12)
            
            # pdf.cell(pdf.get_string_width("Issues"), 7, "Issues", ln=1)
                else:
                    self.set_xy(totalPad + ((maxBoxLength - strLength) / 2), strLevel)
                    self.set_text_color(119,121,123)
                    self.cell(strLength, 7, key, ln=1, align="C")
                
                if issuseLength > maxBoxLength:
                    self.set_xy(totalPad - ((issuseLength - maxBoxLength) / 2), strLevel + 6)
                    pdf.set_font('Arial', '', 12)
                    self.cell(issuseLength, 7, "issues", ln=1, align="C")
                
                else:
                    self.set_xy(totalPad + ((maxBoxLength - issuseLength) / 2), strLevel + 6)
                    pdf.set_font('Arial', '', 12)
                    self.cell(issuseLength, 7, "issues", ln=1, align="C")
                    
                totalPad += maxBoxLength + 30
        def createCompareReport(self, allSeverity):
            keyAllSeverity = allSeverity.values()
            compReport = list(keyAllSeverity)[0:2]
            
            self.cell(0, 7, "Compare with lastest report", ln=1)
            self.set_font('Arial', '', 12)
            self.ln(10)
            maxValue = max(list(compReport[1]["result"].values())[0:-2])
            logger.info(maxValue)
            boxwidth = self.get_string_width(str(maxValue)) + 8
            logger.info(boxwidth)
            
            padding = 0
            curY = self.get_y()
            triUp = """
                <svg width="800px" height="800px" viewBox="0 0 20 20" fill="#000000" xmlns="http://www.w3.org/2000/svg">
                <path d="M11.272 5.205L16.272 13.205C16.8964 14.2041 16.1782 15.5 15 15.5H5.00002C3.82186 15.5 3.1036 14.2041 3.72802 13.205L8.72802 5.205C9.31552 4.265 10.6845 4.265 11.272 5.205Z"/>
                </svg>
            """.encode('utf-8')
            triDown = """
                <svg width="800px" height="800px" viewBox="0 0 20 20" fill="#000000" xmlns="http://www.w3.org/2000/svg">
                <path d="M8.72798 15.795L3.72798 7.795C3.10356 6.79593 3.82183 5.5 4.99998 5.5L15 5.5C16.1781 5.5 16.8964 6.79593 16.272 7.795L11.272 15.795C10.6845 16.735 9.31549 16.735 8.72798 15.795Z"/>
                </svg>
            """.encode('utf-8')
            for key in compReport[1]["result"].keys():
                if key == "severity":
                    continue
                self.set_xy(130, curY + padding-2)
                if compReport[0]['result'][key] > compReport[1]['result'][key]:
                    self.set_fill_color(255, 173, 173)
                    self.image(triUp, x = None, y = None, w = 10, type = '', link = '')
                elif compReport[0]['result'][key] < compReport[1]['result'][key]:
                    self.set_fill_color (173, 239, 173)
                    self.image(triDown, x = None, y = None, w = 10, type = '', link = '')
                
                self.set_xy(130 + boxwidth + 5 , curY + padding)
                self.set_fill_color(getFillColor(threshold=key))
                self.set_text_color(255, 255, 255)
                self.cell(boxwidth, 7, f"{abs(compReport[0]['result'][key]-compReport[1]['result'][key])}", fill=1, align="C")
                
                self.set_xy(130 + boxwidth + 5 + 15 , curY + padding)
                
                self.set_text_color(119,121,123)
                self.cell(0, 7, key, ln=1)
                padding += 13
  
                

            
 
        def create_table(self, table_data, title='', data_size = 10, title_size=12, align_data='L', align_header='L', cell_width='even', x_start='x_default',emphasize_data=[], emphasize_style=None,emphasize_color=(0,0,0), links=[]): 
            """
            table_data: 
                        list of lists with first element being list of headers
            title: 
                        (Optional) title of table (optional)
            data_size: 
                        the font size of table data
            title_size: 
                        the font size fo the title of the table
            align_data: 
                        align table data
                        L = left align
                        C = center align
                        R = right align
            align_header: 
                        align table data
                        L = left align
                        C = center align
                        R = right align
            cell_width: 
                        even: evenly distribute cell/column width
                        uneven: base cell size on lenght of cell/column items
                        int: int value for width of each cell/column
                        list of ints: list equal to number of columns with the widht of each cell / column
            x_start: 
                        where the left edge of table should start
            emphasize_data:  
                        which data elements are to be emphasized - pass as list 
                        emphasize_style: the font style you want emphaized data to take
                        emphasize_color: emphasize color (if other than black) 
            
            """
            default_style = self.font_style
            if emphasize_style == None:
                emphasize_style = default_style
            # default_font = self.font_family
            # default_size = self.font_size_pt
            # default_style = self.font_style
            # default_color = self.color # This does not work

            # Get Width of Columns
            def get_col_widths():
                col_width = cell_width
                if col_width == 'even':
                    col_width = self.epw / len(data[0]) - 1  # distribute content evenly   # epw = effective page width (width of page not including margins)
                elif col_width == 'uneven':
                    col_widths = []

                    # searching through columns for largest sized cell (not rows but cols)
                    for col in range(len(table_data[0])): # for every row
                        longest = 0 
                        for row in range(len(table_data)):
                            cell_value = str(table_data[row][col])
                            value_length = self.get_string_width(cell_value)
                            if value_length > longest:
                                longest = value_length
                        col_widths.append(longest + 4) # add 4 for padding
                    col_width = col_widths



                            ### compare columns 

                elif isinstance(cell_width, list):
                    col_width = cell_width  # TODO: convert all items in list to int        
                else:
                    # TODO: Add try catch
                    col_width = int(col_width)
                return col_width

            # Convert dict to lol
            # Why? because i built it with lol first and added dict func after
            # Is there performance differences?
            if isinstance(table_data, dict):
                header = [key for key in table_data]
                data = []
                for key in table_data:
                    value = table_data[key]
                    data.append(value)
                # need to zip so data is in correct format (first, second, third --> not first, first, first)
                data = [list(a) for a in zip(*data)]

            else:
                header = table_data[0]
                data = table_data[1:]

            line_height = self.font_size * 2.5

            col_width = get_col_widths()
            self.set_font(size=title_size)

            # Get starting position of x
            # Determin width of table to get x starting point for centred table
            if x_start == 'C':
                table_width = 0
                if isinstance(col_width, list):
                    for width in col_width:
                        table_width += width
                else: # need to multiply cell width by number of cells to get table width 
                    table_width = col_width * len(table_data[0])
                # Get x start by subtracting table width from pdf width and divide by 2 (margins)
                margin_width = self.w - table_width
                # TODO: Check if table_width is larger than pdf width

                center_table = margin_width / 2 # only want width of left margin not both
                x_start = center_table
                self.set_x(x_start)
            elif isinstance(x_start, int):
                self.set_x(x_start)
            elif x_start == 'x_default':
                x_start = self.set_x(self.l_margin)


            # TABLE CREATION #

            # add title
            if title != '':
                self.multi_cell(0, line_height, title, border=0, align='j', ln=3, max_line_height=self.font_size)
                self.ln(line_height) # move cursor back to the left margin

            self.set_font(size=data_size)
            # add header
            y1 = self.get_y()
            if x_start:
                x_left = x_start
            else:
                x_left = self.get_x()
            x_right = self.epw + x_left
            if  not isinstance(col_width, list):
                if x_start:
                    self.set_x(x_start)
                for datum in header:
                    self.multi_cell(col_width, line_height, datum, border=0, align=align_header, ln=3, max_line_height=self.font_size)
                    x_right = self.get_x()
                self.ln(line_height) # move cursor back to the left margin
                y2 = self.get_y()
                self.line(x_left,y1,x_right,y1)
                self.line(x_left,y2,x_right,y2)

                for linkIndex, row in enumerate(data):
                    if x_start: # not sure if I need this
                        self.set_x(x_start)
                    for index, datum in enumerate(row):
                        if datum in emphasize_data:
                            self.set_text_color(*emphasize_color)
                            self.set_font(style=emphasize_style)
                            self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3, max_line_height=self.font_size)
                            self.set_text_color(0,0,0)
                            self.set_font(style=default_style)
                        else:
                            if index == 0:
                                self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3, max_line_height=self.font_size, link=links[linkIndex]) # ln = 3 - move cursor to right with same vertical offset # this uses an object named self
                                continue
                            
                            self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3, max_line_height=self.font_size) # ln = 3 - move cursor to right with same vertical offset # this uses an object named self
                    self.ln(line_height) # move cursor back to the left margin
            
            else:
                if x_start:
                    self.set_x(x_start)
                for i in range(len(header)):
                    datum = header[i]
                    self.multi_cell(col_width[i], line_height, datum, border=0, align=align_header, ln=3, max_line_height=self.font_size)
                    x_right = self.get_x()
                self.ln(line_height) # move cursor back to the left margin
                y2 = self.get_y()
                self.line(x_left,y1,x_right,y1)
                self.line(x_left,y2,x_right,y2)


                for i in range(len(data)):
                    if x_start:
                        self.set_x(x_start)
                    row = data[i]
                    for i in range(len(row)):
                        datum = row[i]
                        if not isinstance(datum, str):
                            datum = str(datum)
                        adjusted_col_width = col_width[i]
                        if datum in emphasize_data:
                            self.set_text_color(*emphasize_color)
                            self.set_font(style=emphasize_style)
                            self.multi_cell(adjusted_col_width, line_height, datum, border=0, align=align_data, ln=3, max_line_height=self.font_size)
                            self.set_text_color(0,0,0)
                            self.set_font(style=default_style)
                        else:
                            self.multi_cell(adjusted_col_width, line_height, datum, border=0, align=align_data, ln=3, max_line_height=self.font_size) # ln = 3 - move cursor to right with same vertical offset # this uses an object named self
                    self.ln(line_height) # move cursor back to the left margin
            y3 = self.get_y()
            self.line(x_left,y3,x_right,y3)
            
    
    def createHistoryLineChart(allReports):
        pdf.set_font('Arial', 'B', 13)
        pdf.cell(0, 7, "Reports history over time", ln=1)
        valReport = list(allReports.values())
        y = [[] for _ in range(len(list(valReport[0]["result"].keys()))-1)]
        modification_times = []
        for report_id, report_data in allReports.items():

            modification_time_str = report_data['modification_time'][:-1]  # Remove 'Z' from the end
            modification_time = datetime.fromisoformat(modification_time_str)
            modification_times.append(modification_time)
            item = report_data["result"].values()
            for index, element in enumerate(item):
                if index == len(y):
                    continue
                y[index].append(element)
        # y = np.row_stack((fnx(), fnx(), fnx()))   
        # this call to 'cumsum' (cumulative sum), passing in your y data, 
        # is necessary to avoid having to manually order the datasets
        y = np.flip(np.flip(y, axis=1), axis=0)
        
        x = np.arange(len(list(allReports.values())))
        y_stack = y   # a 3x10 array

        fig = plt.figure()
        # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M:%S'))
        # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        ax1 = fig.add_subplot(111)
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax1.fill_between(x, 0, y_stack[0,:], facecolor="#219C90", alpha=0.75)
        ax1.fill_between(x, 0, y_stack[1,:], facecolor="#E9B824", alpha=0.75)
        ax1.fill_between(x, 0, y_stack[2,:], facecolor="#EE9322", alpha=0.75)
        ax1.fill_between(x, 0, y_stack[3,:], facecolor="#D83F31", alpha=0.75)
        plt.plot(x, y_stack[0,:], color="#219C90", marker='o')
        plt.plot(x, y_stack[1,:], color="#E9B824", marker='o')
        plt.plot(x, y_stack[2,:], color="#EE9322", marker='o')
        plt.plot(x, y_stack[3,:], color="#D83F31", marker='o')
        ax1.set_xlim(0)
        # ax1.set_xlim(min(modification_times))
        ax1.set_ylim(0)
        plt.ylabel('Number of vulnerabilities')
        plt.xticks(x, modification_times[::-1], rotation=-30)
        ax1.grid(True)

        plt.tight_layout()
        # Format x-axis labels as dates
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return buf
    
    def getFillColor(severity=None, threshold = None, hex = False):
        def hex_to_rgb(hex_code):
            hex_code = hex_code.lstrip('#')  # Remove the hash symbol if it exists
            return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))
        if hex:
            if threshold == "Critical":
                return '#D83F31'
            elif threshold == "High":
                return '#EE9322'
            elif threshold == "Medium":
                return '#E9B824'
            else:
                return '#219C90'
            
        if threshold != None:
            if threshold == "Critical":
                return hex_to_rgb('#D83F31')
            elif threshold == "High":
                return hex_to_rgb('#EE9322')
            elif threshold == "Medium":
                return hex_to_rgb('#E9B824')
            else:
                return hex_to_rgb('#219C90')
            
        fSeverity = float(severity)
        if hex:
            if fSeverity >= 9.0:
                return '#D83F31'
            elif fSeverity >= 7.0:
                return '#EE9322'
            elif fSeverity >= 4.0:
                return '#E9B824'
            else:
                return '#219C90'

        if fSeverity >= 9.0:
            return hex_to_rgb('#D83F31')
        elif fSeverity >= 7.0:
            return hex_to_rgb('#EE9322')
        elif fSeverity >= 4.0:
            return hex_to_rgb('#E9B824')
        else:
            return hex_to_rgb('#219C90')
        
        
    def createStackedBarChart(familys):
        species = familys.get("familysName")
        weight_counts = familys.get("count")
        width = 0.5

        fig, ax = plt.subplots()
        previous = [0 for _ in range(len(species))]
        b = []
        for boolean, weight_count in weight_counts.items():
            color = getFillColor(threshold=boolean, hex=True)
            p = ax.barh(species, weight_count, left=previous, color=color)
            previous = weight_count
            b.append(p)


        ax.legend(b, list(weight_counts.keys()), loc="lower right")
        # x axis is interger
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        for p in ax.patches:
            width, height = p.get_width(), p.get_height()
            x, y = p.get_xy() 
            if width > 0:
                ax.text(x+width/2, 
                        y+height/2, 
                        '{:.0f}'.format(width), 
                        horizontalalignment='center', 
                        verticalalignment='center',
                        color='white',
                        fontsize=14
                        )
                
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return buf
    
    def createGaugeChart(data):
        colors = ['#219C90',"#E9B824","#EE9322","#D83F31"]

        values = [10.0,9.0,7.0,4.0,0.0]

        fig = plt.figure(figsize=(18,18))

        ax = fig.add_subplot(projection="polar");

        ax.bar(x=[ 1.884,0.942,0.314,0  ], width=[1.256,0.942,0.628,0.314], height=0.5, bottom=1,
            linewidth=8, edgecolor="white",
            color=colors, align="edge");

        for loc, val in zip([0, 0.314, 0.942, 1.884, 3.14], values):
            plt.annotate(val, xy=(loc, 1.5), fontsize=30, ha="right" if val<=4.0 else "left");

        score = data.get('allHostResult').get("summary").get("severity")
        if float(score) == -99.0:
            score = 0
        plt.annotate( score, xytext=(0,0), xy=(3.14 - (float(score) / 10 * 3.14), 1.35),
                    arrowprops=dict(arrowstyle="wedge, tail_width=0.5", color="black", shrinkA=0),
                    bbox=dict(boxstyle="circle", facecolor="black", linewidth=2.0, ),
                    fontsize=90, color="white", ha="center"
                    );


        plt.title("Scored by CVSS v3.0", loc="center",pad=30, fontsize=35, fontweight="bold");
        ax.set_thetamin(0)
        ax.set_thetamax(180)
        ax.set_axis_off()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return buf
    
    def getDeltaComapare(data):
        allKey = list(data.keys())
        lastestReport = data[allKey[-1]]
        pass
        
    
    def getSeverityInfo(severity):
        fSeverity = float(severity)
        if fSeverity >= 9.0:
            return "Critical issues signify high risk; even amateurs can exploit them, posing a severe breach threat. Automated tools often target these vulnerabilities, elevating breach risks significantly. Immediate fixes are crucial to prevent unauthorized access, ensuring robust security."
        elif fSeverity >= 7.0:
            return "High-risk vulnerabilities demand swift attention. Attackers could exploit them, potentially causing significant harm. Rapid action is essential to safeguard systems and sensitive data effectively, maintaining a strong security posture."
        elif fSeverity >= 4.0:
            return "Medium-risk issues represent a notable security concern. While not as exploitable as critical vulnerabilities, they still pose a threat. Addressing these promptly is essential to mitigate risks effectively, enhancing overall system security against potential breaches."
        else:
            return "Addressing low-risk vulnerabilities is fundamental for comprehensive security. Even though less severe, they shouldn't be ignored. Regular updates and vigilant monitoring fortify defenses, ensuring systems are protected against opportunistic threats."

    try :
        pdf = PDF('p', 'mm', 'A4')
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, ln=1)
        
        if isDeltaReport:
            allReports = data.get("severityPerReport")
            def get_modification_time(report_id):
                return allReports[report_id]['modification_time']
            lastest_report_id = max(allReports, key=get_modification_time)
            lastestReport = allReports[lastest_report_id]
            modificationTime = lastestReport['modification_time']
            allHostSummary = lastestReport["result"]
            severity = allHostSummary["severity"]
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(getFillColor(severity=severity))
            pdf.set_draw_color(getFillColor(severity=severity))
            date = datetime.strptime(modificationTime, "%Y-%m-%dT%H:%M:%SZ")
            pdf.multi_cell(0, 7, f"Scan Summary: {data.get('name')}\n {date.strftime('%d %B %Y')}",border=1 ,ln=1,fill=1, align='C')
            y = pdf.get_y()
            pdf.set_text_color(119,121,123)
            pdf.set_font('Arial', 'B', 16)
            pdf.multi_cell(0, 10, f'\n\n{getSeverityThreshold(severity)} ( {severity} )', align="C",border="L,R", ln=1)
            pdf.set_font('Arial', 'B', 13)
            
            pdf.cell(0, 5, "Threat Level" ,ln=1, align="C", border="L,R")
            pdf.cell(0, 7, ln=1, border="L,R")
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 5, getSeverityInfo(severity), align="C",border="L,R", ln=1)
            yBox = pdf.get_y()
            pdf.multi_cell(0, 7, "\n\n\n\n\n\n" , ln=1, border="L,R,B")
            pdf.set_y(yBox+10)
            pdf.createBox(allHostSummary)
            outBox = pdf.get_y()
            
            # pdf.set_fill_color(getFillColor(4))
            
            # pdf.set_text_color(255, 255, 255)
            # pdf.set_font('Arial', 'B', 13)
            # pdf.multi_cell(pdf.get_string_width(allHostSummary.get('Medium')) + 10, pdf.get_string_width(allHostSummary.get('Medium')) + 10, f"{allHostSummary.get('Medium')}", align="C",fill=1 , ln=1)
            
            # pdf.set_text_color(119,121,123)
            # pdf.cell(pdf.get_string_width("Medium"), 7, "Medium", ln=1)
            # pdf.set_font('Arial', '', 12)
            
            # pdf.cell(pdf.get_string_width("Issues"), 7, "Issues", ln=1)
            pdf.set_xy((pdf.w- 15) /2, y + 5)
            pdf.set_fill_color(getFillColor(severity=severity))
            svgCode ="""<svg fill="#000000" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
                width="800px" height="800px" viewBox="0 0 30 30" xml:space="preserve">
            <g>
                <path d="M11.001,30l2.707-16.334H5L11.458,0l9.25,0.123L16.667,8H25L11.001,30z"/>
            </g>
            </svg>
            """.encode('utf-8')
            pdf.image(svgCode, x = None, y = None, w = 15, type = '', link = '')
            pdf.set_y(outBox + 25)
            pdf.image(createHistoryLineChart(allReports), x = None, y = None, w=100, type = '', link = '')
            pdf.set_xy(115, outBox + 25)
            pdf.createCompareReport(allReports)
            getDeltaComapare(allReports)
            return bytes(pdf.output())
        
        # genarate pdf
        
       
        
        logger.info(data)
        pdf.set_x((pdf.w - 75) / 2)
        pdf.image(createGaugeChart(data), x = None, y = None, w = 75, type = '', link = '')
        
        # pdf.set_x(((pdf.w * 0.2) + 170) / 2)
        # x = pdf.get_x()
        pdf.set_x(pdf.l_margin)
        pdf.cell(0, 7, "Report name : " + data.get('name'), ln=1, align="C")
        # y1 = pdf.get_y()
        
        pdf.set_font('Arial', '', 10)
        # pdf.set_x(x)

        pdf.cell(40, 7, "Created on : "+ datetime.today().date().strftime('%d/%m/%Y') ,ln=1)
        # pdf.set_x(x)
        
        pdf.cell(40, 7, "Target Host Information: " + data.get('targetHost'),ln=1)
        pdf.ln(10)
        
        #prepare data
        header = ["IP Address"]
        for key in data.get("allHostResult").get("summary").keys():
            header.append(key)
            
        result = [header]
        links = {}
        
        for ip, values in data.get("allHostResult").items():
            if ip == "summary":
                continue
            row = [ip]
            links[ip] = pdf.add_link()
            for key in values.keys():
                if key == "results":
                    continue
                row.append(str(values[key]))
            result.append(row)
        pdf.create_table(table_data = result, cell_width='even', links=list(links.values()))
        pdf.ln(5)
        pdf.cell(0, 7, "Vulnerability by family", ln=1, align="C")
        pdf.image(createStackedBarChart(data.get("familys")), x = (pdf.w - 90) /2, y = None, w = 90, type = '', link = '')
        # y2 = pdf.get_y()
        # pdf.set_xy((pdf.w * 0.2) / 2, abs(y2-y1 + 75/4)/2)
        pdf.add_page()
        pdf.set_font('Arial', 'B', 22)
        pdf.ln(10)
        pdf.cell(0, 7, "Vulnerability Summary", ln=1, align="C")
        for page, host in enumerate(list(data.get("allHostResult").keys())):
            if host == "summary":
                continue
            pdf.set_font('Arial', 'B', 16)
            pdf.set_link(links[host])
            pdf.ln(7)    
            pdf.cell(0, 7, f'Host : {host},  Overall severity score : {data.get("allHostResult").get(host).get("severity")}',ln=1)
            
            for result in data.get("allHostResult").get(host).get("results"):
                with pdf.unbreakable() as doc:
                    doc.set_fill_color(getFillColor(severity=result.get("severity")))
                    doc.set_draw_color(getFillColor(severity=result.get("severity")))
                    doc.ln(7)
                    doc.set_font('Arial', 'B', 12)
                    doc.multi_cell(0, 7, f'{result.get("name")}',ln=1, fill=1, border="L,R,T")
                    doc.set_font('Arial', '', 12)
                    doc.cell(0,3, ln=1,border="L,R")
                    
                    doc.set_font('Arial', 'B', 12)
                    doc.multi_cell(0, 7, f'CVSS score : {result.get("severity")}',ln=1, border="L,R")
                    doc.cell(0,3, ln=1,border="L,R")
                    
                    
                    doc.cell(0,3, ln=1,border="L,T,R")
                    doc.set_font('Arial', 'B', 12)
                    doc.cell(0, 7, "Summary",ln=1, border="L,R")
                    doc.set_font('Arial', '', 12)
                    doc.multi_cell(0, 7, result.get("summary"),ln=1, border="L,R")
                    doc.cell(0,3, ln=1,border="L,B,R")
                    
                    doc.cell(0,3, ln=1,border="L,T,R")
                    doc.set_font('Arial', 'B', 12)
                    doc.cell(0, 7, "Solution",ln=1, border="L,R")
                    doc.set_font('Arial', '', 12)
                    doc.multi_cell(0, 7, result.get("solution"),ln=1, border="L,R")
                    doc.cell(0,3, ln=1,border="L,R,B")
                
            if page != len(list(data.get("allHostResult").keys())) - 1:
                pdf.add_page()
            
        # utc_time_str = data.get("mostVul").get("created")
        # utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
        # utc_offset = timedelta(hours=7)
        # local_time = utc_time + utc_offset
        # pdf.cell(0, 7, "Scanned on : " + str(local_time) ,ln=1)

        # bubble_chart = BubbleChart(area=data.get("familys").get("count"),
        #                    bubble_spacing=0.1)

        # bubble_chart.collapse()

        # fig, ax = plt.subplots(subplot_kw=dict(aspect="equal"))
        # bubble_chart.plot(
        #     ax, data.get("familys").get("familysName"), data.get("familys").get("color"))
        # ax.axis("off")
        # ax.relim()
        # ax.autoscale_view()
        # ax.set_title('Vulnerability by family', fontsize=20, fontweight="bold")
        # buf = io.BytesIO()
        # plt.savefig(buf, format='png')
        # buf.seek(0)
        # pdf.set_x((pdf.w-125)/2)
        # pdf.image(buf, x = None, y = None, w=125, type = '', link = '')
        
        return bytes(pdf.output())
    except Exception as e:
        logger.error(e)
        raise RuntimeError('error when create pdf')