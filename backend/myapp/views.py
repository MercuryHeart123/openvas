from django.apps import apps
from utils.xmlUtil import xmlToJson
import logging
from xml.etree import cElementTree as ET
from xml.etree import ElementTree
from fpdf import FPDF, HTMLMixin
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
import numpy as np
import pytz

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
def logout(token):
    response = gvm_service.logout(token)
    return response

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
def getMostVulnerability(report):
    data = report.findall('./report/report/results/result')
    mostScore = data[0]
    tags = mostScore.find('./nvt/tags').text
    parts = tags.split("|")
    for part in parts:
        if part.startswith("summary="):
            desired_text = part[len("summary="):]
            break
    data_dict = {
        "name" : mostScore.find('./name').text,
        "host" : mostScore.find('./host').text,
        "severity" : mostScore.find('./severity').text,
        "summary" : desired_text,
        "solution" : mostScore.find('./nvt/solution').text,
        "created" : mostScore.find('./creation_time').text,
    }
    return data_dict

def getFamily(report):
    allFamily = report.findall('./report/report/results/result/nvt/family')
    familysName = []
    count = []
    for family in allFamily:
        if family.text not in familysName:
            familysName.append(family.text)
            count.append(1)
        else:
            index = familysName.index(family.text)
            count[index] += 1
    index = 0
    tmp = []
    for family in familysName:
        tmp.append(family + " (" + str(count[index]) + ")")
        index += 1
        
        
    return {"familysName":tmp, "count":count, 'color': ['#5A69AF', '#579E65', '#F9C784', '#FC944A', '#F24C00', '#00B825']}
        
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
        mostVul = getMostVulnerability(reportXml)
        familys = getFamily(reportXml)
        obj = {'name': name, 'targetHost': targetHost, 'allHostResult': allHostResult, 'mostVul': mostVul, 'familys':familys}
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
            
    class BubbleChart:
        def __init__(self, area, bubble_spacing=0):
            """
            Setup for bubble collapse.

            Parameters
            ----------
            area : array-like
                Area of the bubbles.
            bubble_spacing : float, default: 0
                Minimal spacing between bubbles after collapsing.

            Notes
            -----
            If "area" is sorted, the results might look weird.
            """
            area = np.asarray(area)
            r = np.sqrt(area / np.pi)

            self.bubble_spacing = bubble_spacing
            self.bubbles = np.ones((len(area), 4))
            self.bubbles[:, 2] = r
            self.bubbles[:, 3] = area
            self.maxstep = 2 * self.bubbles[:, 2].max() + self.bubble_spacing
            self.step_dist = self.maxstep / 2

            # calculate initial grid layout for bubbles
            length = np.ceil(np.sqrt(len(self.bubbles)))
            grid = np.arange(length) * self.maxstep
            gx, gy = np.meshgrid(grid, grid)
            self.bubbles[:, 0] = gx.flatten()[:len(self.bubbles)]
            self.bubbles[:, 1] = gy.flatten()[:len(self.bubbles)]

            self.com = self.center_of_mass()

        def center_of_mass(self):
            return np.average(
                self.bubbles[:, :2], axis=0, weights=self.bubbles[:, 3]
            )

        def center_distance(self, bubble, bubbles):
            return np.hypot(bubble[0] - bubbles[:, 0],
                            bubble[1] - bubbles[:, 1])

        def outline_distance(self, bubble, bubbles):
            center_distance = self.center_distance(bubble, bubbles)
            return center_distance - bubble[2] - \
                bubbles[:, 2] - self.bubble_spacing

        def check_collisions(self, bubble, bubbles):
            distance = self.outline_distance(bubble, bubbles)
            return len(distance[distance < 0])

        def collides_with(self, bubble, bubbles):
            distance = self.outline_distance(bubble, bubbles)
            return np.argmin(distance, keepdims=True)

        def collapse(self, n_iterations=50):
            """
            Move bubbles to the center of mass.

            Parameters
            ----------
            n_iterations : int, default: 50
                Number of moves to perform.
            """
            for _i in range(n_iterations):
                moves = 0
                for i in range(len(self.bubbles)):
                    rest_bub = np.delete(self.bubbles, i, 0)
                    # try to move directly towards the center of mass
                    # direction vector from bubble to the center of mass
                    dir_vec = self.com - self.bubbles[i, :2]

                    # shorten direction vector to have length of 1
                    dir_vec = dir_vec / np.sqrt(dir_vec.dot(dir_vec))

                    # calculate new bubble position
                    new_point = self.bubbles[i, :2] + dir_vec * self.step_dist
                    new_bubble = np.append(new_point, self.bubbles[i, 2:4])

                    # check whether new bubble collides with other bubbles
                    if not self.check_collisions(new_bubble, rest_bub):
                        self.bubbles[i, :] = new_bubble
                        self.com = self.center_of_mass()
                        moves += 1
                    else:
                        # try to move around a bubble that you collide with
                        # find colliding bubble
                        for colliding in self.collides_with(new_bubble, rest_bub):
                            # calculate direction vector
                            dir_vec = rest_bub[colliding, :2] - self.bubbles[i, :2]
                            dir_vec = dir_vec / np.sqrt(dir_vec.dot(dir_vec))
                            # calculate orthogonal vector
                            orth = np.array([dir_vec[1], -dir_vec[0]])
                            # test which direction to go
                            new_point1 = (self.bubbles[i, :2] + orth *
                                        self.step_dist)
                            new_point2 = (self.bubbles[i, :2] - orth *
                                        self.step_dist)
                            dist1 = self.center_distance(
                                self.com, np.array([new_point1]))
                            dist2 = self.center_distance(
                                self.com, np.array([new_point2]))
                            new_point = new_point1 if dist1 < dist2 else new_point2
                            new_bubble = np.append(new_point, self.bubbles[i, 2:4])
                            if not self.check_collisions(new_bubble, rest_bub):
                                self.bubbles[i, :] = new_bubble
                                self.com = self.center_of_mass()

                if moves / len(self.bubbles) < 0.1:
                    self.step_dist = self.step_dist / 2

        def plot(self, ax, labels, colors):
            """
            Draw the bubble plot.

            Parameters
            ----------
            ax : matplotlib.axes.Axes
            labels : list
                Labels of the bubbles.
            colors : list
                Colors of the bubbles.
            """
            for i in range(len(self.bubbles)):
                circ = plt.Circle(
                    self.bubbles[i, :2], self.bubbles[i, 2], color=colors[i])
                ax.add_patch(circ)
                ax.text(*self.bubbles[i, :2], labels[i],
                        horizontalalignment='center', verticalalignment='center')
                
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


        plt.title("Scored by CVSS v3.0", loc="center",pad=30, fontsize=35, fontweight="bold");
        ax.set_thetamin(0)
        ax.set_thetamax(180)
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
        pdf.set_xy((pdf.w * 0.2) / 2, abs(y2-y1 + 75/4)/2)
        pdf.image(buf, x = None, y = None, w = 75, h = 75, type = '', link = '')
        pdf.set_font('Arial', 'B', 10)
        
        pdf.cell(0, 7, "The most vulnerability that need to fix is on host " + data.get("mostVul").get("host"),ln=1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 7, data.get("mostVul").get("name"),ln=1)
        pdf.cell(0, 7, "CVSS score : " + data.get("mostVul").get("severity"),ln=1)
        pdf.cell(0, 7, "Summary : " + data.get("mostVul").get("summary"),ln=1)
        pdf.cell(0, 7, "Solution : " + data.get("mostVul").get("solution"),ln=1)
        
        utc_time_str = data.get("mostVul").get("created")
        utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
        utc_offset = timedelta(hours=7)
        local_time = utc_time + utc_offset
        pdf.cell(0, 7, "Scanned on : " + str(local_time) ,ln=1)

        bubble_chart = BubbleChart(area=data.get("familys").get("count"),
                           bubble_spacing=0.1)

        bubble_chart.collapse()

        fig, ax = plt.subplots(subplot_kw=dict(aspect="equal"))
        bubble_chart.plot(
            ax, data.get("familys").get("familysName"), data.get("familys").get("color"))
        ax.axis("off")
        ax.relim()
        ax.autoscale_view()
        ax.set_title('Vulnerability by family', fontsize=20, fontweight="bold")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        pdf.set_x((pdf.w-125)/2)
        pdf.image(buf, x = None, y = None, w=125, type = '', link = '')
        
        return bytes(pdf.output())
    except Exception as e:
        logger.error(e)
        raise RuntimeError('error when create pdf')