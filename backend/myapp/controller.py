from . import views
from django.http import JsonResponse
from django.http import HttpResponse
import openvas.getTask as openvas
from utils.xmlUtil import xmlToJson
import json
from xml.etree.ElementTree import Element, SubElement, tostring
import logging
import random
from fpdf import FPDF
import matplotlib.pyplot as plt
import io

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
def dowloadReportController(request):
     # Create a new workbook and add a worksheet
    decoded_str = request.body.decode()
    data_dict = json.loads(decoded_str)
    colors = ['#4dab6d',"#f6ee54","#fabd57","#ee4d55"]

    values = [10.0,9.0,7.0,4.0,0.0]

    fig = plt.figure(figsize=(18,18))

    ax = fig.add_subplot(projection="polar");

    ax.bar(x=[ 1.884,0.942,0.314,0  ], width=[1.256,0.942,0.628,0.314], height=0.5, bottom=2,
        linewidth=8, edgecolor="white",
        color=colors, align="edge");

    # plt.annotate("High Performing", xy=(0.16,2.1), rotation=-75, color="white", fontweight="bold");
    # plt.annotate("Sustainable", xy=(0.65,2.08), rotation=-55, color="white", fontweight="bold");
    # plt.annotate("Maturing", xy=(1.14,2.1), rotation=-32, color="white", fontweight="bold");
    # plt.annotate("Developing", xy=(1.62,2.2), color="white", fontweight="bold");
    # plt.annotate("Foundational", xy=(2.08,2.25), rotation=20, color="white", fontweight="bold");
    # plt.annotate("Volatile", xy=(2.46,2.25), rotation=45, color="white", fontweight="bold");
    # plt.annotate("Unsustainable", xy=(3.0,2.25), rotation=75, color="white", fontweight="bold");

    for loc, val in zip([0, 0.314, 0.942, 1.884, 3.14], values):
        plt.annotate(val, xy=(loc, 2.5), ha="right" if val<=0 else "left");

    plt.annotate("10.0", xytext=(0,0), xy=(0.1, 2.35),
                arrowprops=dict(arrowstyle="wedge, tail_width=0.5", color="black", shrinkA=0),
                bbox=dict(boxstyle="circle", facecolor="black", linewidth=2.0, ),
                fontsize=45, color="white", ha="center"
                );


    plt.title("Performance Gauge Chart", loc="center", pad=20, fontsize=35, fontweight="bold");
    ax.set_axis_off();
    # obj = views.getData(data_dict.get('reportId'), data_dict.get('token'))
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    pdf = FPDF('p', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Hello World!',ln=1)
    pdf.image(buf, x = None, y = None, w = 125, h = 125, type = '', link = '')
    response = HttpResponse(bytes(pdf.output()), content_type='application/pdf')
    response['Content-Disposition'] = "attachment; filename=myfilename.pdf"
    # wb = Workbook()
    # ws = wb.active
    
    # # Add headers
    # ws.merge_cells('B3:E4')
    # ws["B3"].value = "Terabyte vulnerability\nAssessment report"
    # ws["B3"].alignment = Alignment(wrapText=True)
    # ws["B8"].value = f"{obj.get('name')}: {datetime.now().strftime('%d/%m/%Y')}"

    # ws["B10"].value = "Target Host Information:"
    # ws["B11"].value = obj.get('targetHost')
    
    # data_list = [{"IP Address": ip, **values} for ip, values in obj.get('allHostResult').items()]
    # startChar = 'B'
    # column = list(data_list[0].keys())
    # for i in range(0, len(data_list[0])):
    #     currentChar = chr(ord(startChar) + i)
    #     ws[f"{currentChar}{13}"].value = column[i]
    #     for j in range(0, len(data_list)):
    #         ws[f"{currentChar}{14 + j}"].value = data_list[j][column[i]]
    
    # mediumStyle = openpyxl.worksheet.table.TableStyleInfo(name='TableStyleMedium2',
    #                                                   showRowStripes=True)
    
    # table = openpyxl.worksheet.table.Table(ref=f'B13:{get_column_letter(len(column)+1)}{len(data_list) + 13}',
    #                                    displayName='FruitColors',
    #                                    tableStyleInfo=mediumStyle)
    # # Create a response with the XLSX content
    # ws.add_table(table)

    # for row, text in enumerate([39,30,20,11,100], start=4):
    #     ws.cell(column=8, row=row, value=text)
    
    # for row, text in enumerate([(float(ws["F14"].value)*10)-1,1,200-(float(ws["F14"].value)*10)], start=4):
    #     ws.cell(column=9, row=row, value=text)
        
    # c1 = DoughnutChart(firstSliceAng=270, holeSize=50)
    # c1.title = f"Scored by CVSS v3.0\n scored : {ws['F14'].value}"
    # c1.legend = None
    # ref = Reference(ws, min_col=8, min_row=4, max_row=8)

    # s1 = Series(ref, title_from_data=False)

    # slices = [DataPoint(idx=i) for i in range(5)]
    # slices[0].graphicalProperties.solidFill = "80C701" # red
    
    # slices[1].graphicalProperties.solidFill = "F7C914" # yellow
    # slices[2].graphicalProperties.solidFill = "F67500" # blue
    # slices[3].graphicalProperties.solidFill = "E9390C"
    # slices[4].graphicalProperties.noFill = True # invisible

    # s1.data_points = slices
    # c1.series = [s1]

    
    # c2 = PieChart(firstSliceAng=270)
    # c2.legend = None

    # ref = Reference(ws, min_col=9, min_row=4, max_col=9, max_row=6)
    # s2 = Series(ref, title_from_data=False)

    # slices = [DataPoint(idx=i) for i in range(3)]
    # slices[0].graphicalProperties.noFill = True # invisible
    # slices[1].graphicalProperties.solidFill = "000000" # black needle
    # slices[2].graphicalProperties.noFill = True # invisible
    # s2.data_points = slices
    # c2.series = [s2]
    
    # c1 += c2
    # c1.width = 7.493 
    # ws.add_chart(c1, "H3")
    # response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    # response['Content-Disposition'] = 'attachment; filename="items.xlsx"'

    # # Save the workbook to the response
    # wb.save(response)

    return response
    
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
            result = views.getUpdate(request.GET.get('token', ''))
            # logger.info(request.GET.get('token', ''))
            # root = Element('envelope')
            # child = SubElement(root, "version")

            # child.text = "22.06.0"
            # nvts = SubElement(root, "nvts")
            # cves = SubElement(root, "cves")
            # certs = SubElement(root, "certs")
            # for i in range(0, 7):
            #     nvt = SubElement(nvts, "nvt")
            #     nvt.attrib['oid'] = f"{i}"
            #     nvt.text = f"{random.randint(0, 100)}"
            #     cve = SubElement(cves, "cve")
            #     cve.attrib['oid'] = f"{i}"
            #     cve.text = f"{random.randint(0, 100)}"
            #     cert = SubElement(certs, "cert")
            #     cert.attrib['oid'] = f"{i}"
            #     cert.text = f"{random.randint(0, 100)}"

            result = tostring(result).decode('utf-8')
            statusCode = 200
        else:
            raise BaseException("Method not allowed")

    except Exception as e:
        result = str(e)
        logger.error(e)
        
        statusCode = 500

    return HttpResponse(result, status=statusCode, content_type='application/xml')

