from django.apps import apps
from utils.xmlUtil import xmlToJson
import logging
from xml.etree import cElementTree as ET
from xml.etree import ElementTree
from fpdf import FPDF, HTMLMixin
import matplotlib.pyplot as plt
import io
from datetime import datetime

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
        return RuntimeError('token is required')
    
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

def getPdf(data):
    class PDF(FPDF, HTMLMixin):
        def header(self):
            
            self.set_font('Arial', 'B', 14)
            self.image('slogo.png', 10, 8, 13)
            self.set_x(25)
            self.cell(self.get_string_width("Terabyte vulnerability"), 5, "Terabyte vulnerability",ln=1)
            self.set_x(25)
            
            self.cell(self.get_string_width("Assessment report"), 5, "Assessment report",ln=1)
            self.cell(0,5, border="B",ln=1)

        def create_table(self, table_data, title='', data_size = 10, title_size=12, align_data='L', align_header='L', cell_width='even', x_start='x_default',emphasize_data=[], emphasize_style=None,emphasize_color=(0,0,0)): 
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

                for row in data:
                    if x_start: # not sure if I need this
                        self.set_x(x_start)
                    for datum in row:
                        if datum in emphasize_data:
                            self.set_text_color(*emphasize_color)
                            self.set_font(style=emphasize_style)
                            self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3, max_line_height=self.font_size)
                            self.set_text_color(0,0,0)
                            self.set_font(style=default_style)
                        else:
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
            
            
    try :
        colors = ['#4dab6d',"#f6ee54","#fabd57","#ee4d55"]

        values = [10.0,9.0,7.0,4.0,0.0]

        fig = plt.figure(figsize=(18,18))

        ax = fig.add_subplot(projection="polar");

        ax.bar(x=[ 1.884,0.942,0.314,0  ], width=[1.256,0.942,0.628,0.314], height=0.5, bottom=1,
            linewidth=8, edgecolor="white",
            color=colors, align="edge");

        for loc, val in zip([0, 0.314, 0.942, 1.884, 3.14], values):
            plt.annotate(val, xy=(loc, 1.5), fontsize=30, ha="right" if val<=4.0 else "left");

        score = list(data.get('allHostResult').items())[0][1].get('severity')
        if float(score) == -99.0:
            score = 0
        plt.annotate( score, xytext=(0,0), xy=(3.14 - (float(score) / 10 * 3.14), 1.35),
                    arrowprops=dict(arrowstyle="wedge, tail_width=0.5", color="black", shrinkA=0),
                    bbox=dict(boxstyle="circle", facecolor="black", linewidth=2.0, ),
                    fontsize=90, color="white", ha="center"
                    );


        plt.title("Scored by CVSS v3.0", loc="center", pad=20, fontsize=35, fontweight="bold");
        ax.set_axis_off()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # genarate pdf
        
        pdf = PDF('p', 'mm', 'A4')
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, ln=1)
        
        
        pdf.set_x(((pdf.w * 0.2) + 170) / 2)
        x = pdf.get_x()

        pdf.cell(40, 7, "Report name : " + data.get('name'), ln=1)
        y1 = pdf.get_y()
        
        pdf.set_font('Arial', '', 10)
        pdf.set_x(x)

        pdf.cell(40, 7, "Created on : "+ datetime.today().date().strftime('%d/%m/%Y') ,ln=1)
        pdf.set_x(x)
        
        pdf.cell(40, 7, "Target Host Information: " + data.get('targetHost'),ln=1)
        pdf.ln(10)
        header = ["IP Address", "High", "Medium","Low", "Severity"]
        result = [header]
        for ip, values in data.get("allHostResult").items():
            row = [ip, values.get("High"), values.get("Medium"), values.get("Low"),  values.get("severity")]
            result.append(row)
        
        pdf.create_table(table_data = result,x_start=x, cell_width='uneven')
        y2 = pdf.get_y()
        pdf.cell(40, 7, "test",ln=1)
        
        pdf.set_xy((pdf.w * 0.2) / 2, abs(y2-y1 + 75/2)/2)
        pdf.image(buf, x = None, y = None, w = 75, h = 75, type = '', link = '')
        return bytes(pdf.output())
    except Exception as e:
        logger.error(e)
        raise RuntimeError('error when create pdf')