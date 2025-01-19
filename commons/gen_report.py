from io import BytesIO
from reportlab.lib.pagesizes import letter, A4, LETTER
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, Paragraph, PageTemplate, Frame, TableStyle, Table, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import blue, black, red, white, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import shapes
from datetime import datetime
import json, os
from insightfaces.main import FaceAI
from commons.common import Common
from cryptophic.main import decrypt_file_to
from commons.db_connection import DBConnection
from commons.ntptime import ntp_get_time_from_object
from commons.systimer import SysTimer

class GenReport:
    def __init__(self, buffer, probid):
        self.buffer = buffer
        self.pagesize = (8.5 * inch, 14 * inch)
        self.width, self.height = self.pagesize
        self.margin_x = 0.4 * inch
        self.margin_y = 0.5 * inch
        self.probid = probid
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

    def _header_footer(self, canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
 
        # Header
        header = Paragraph('FaceAI Probe Report', ParagraphStyle(name="style", fontName="Arial", fontSize=14, alignment=TA_CENTER, textColor=HexColor(0x0070C0)))
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
        header = Paragraph('Probe ID: %s'%self.probid, ParagraphStyle(name="style", fontName="Arial", fontSize=12, alignment=TA_CENTER, textColor=black))
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h * 2.9)
 
        # Footer
        footer = Paragraph('', ParagraphStyle(name="style", fontName="Arial", fontSize=12, alignment=TA_RIGHT, textColor=black))
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)
 
        # Release the canvas
        canvas.restoreState()


    def print_reports(self, reportinfo):
        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=self.margin_x,
                                leftMargin=self.margin_x,
                                topMargin=self.margin_y * 2.4,
                                bottomMargin=self.margin_y,
                                pagesize=self.pagesize)
 
        # Our container for 'Flowable' objects
        elements = []
 
        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
 
        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        textsize = 12
        leading = 14
        spacing = 6
        nb_spacing = 12
        # elements.append(Paragraph('''<para align=center leading=18 fontName='Arial'><font size=12 color=0xff0000><b>''' + 'Probe result: ' + reportinfo["result"] + '''</b></font></para>'''))
        elements.append(Paragraph('Probe result: ' + reportinfo["result"], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_CENTER, textColor=red, leading=20)))

        tablestyle1 = TableStyle([
            ('GRID', (0,0), (-1,-1), 1.0, white),
            ('VALIGN', (0, 0), (0, 0), 'TOP'), 
            ('VALIGN', (-1, -1), (-1, -1), 'CENTER'), 
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ])
        nested1 = [
            Paragraph('Time of report generation: ' + reportinfo["created"], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
            Paragraph('Case no.:' + reportinfo["casenum"], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
            Paragraph('PS: ' + reportinfo["ps"], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
            Paragraph('Examiner’s name: ' + reportinfo["examname"], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
            Paragraph('Examiner’s no.: ' + reportinfo["examnum"], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
            Paragraph('Remarks: ' + reportinfo["remarks"] * 5, ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading))
        ]   
        img = Image(reportinfo["subject"])
        img._restrictSize(3.6*inch, 3.0*inch)
        img.hAlign = TA_CENTER
        img.vAlign = TA_CENTER
        nested2 = [
            img,
            Paragraph('Subject photo', ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_CENTER, textColor=black, leading=leading))
        ]
        table1 = Table([[nested1, nested2]],
                  colWidths=('50%', '50%'),
                  rowHeights=None,
                  style=tablestyle1)
        elements.append(table1)

        elements.append(Paragraph(reportinfo['description'], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading, spaceBefore=spacing, spaceAfter=spacing)))

        nested = {}
        targets_len = len(reportinfo["targets"])
        tablestyle2 = TableStyle([
            ('GRID', (0,0), (-1,-1), 1.0, white),
            ('VALIGN', (0, 0), (-1, -1), 'CENTER'), 
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ])
        for index, target in enumerate(reportinfo["targets"]):  
            img = Image(target['path'])
            img._restrictSize(3.6*inch, 3.0*inch)
            img.hAlign = TA_CENTER
            img.vAlign = TA_CENTER

            if img.imageWidth > img.imageHeight:
                rate = img.drawWidth / img.imageWidth
            else:
                rate = img.drawHeight / img.imageHeight

            draw = shapes.Drawing(img.drawWidth, 0)
            rect = shapes.Rect(target['face_rect']['left']*rate, (img.drawHeight-target['face_rect']['top']*rate-target['face_rect']['height']*rate), target['face_rect']['width']*rate, target['face_rect']['height']*rate, fillColor=None, strokeColor=red)
            draw.add(rect)

            if target['oldcase']:
                nested[index % 2] = [
                    img,
                    draw,
                    Paragraph('Serial Number: %d'%(index + 1), ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
                    Paragraph('Similarity score: %.2f%% (%s)'%(target['sim'], FaceAI.get_similarity_str([], target['sim'], "", 100)), ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
                    Paragraph('Old Case Number: %s'%target['caseno'], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
                    Paragraph('PS: %s'%target['ps'], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
                    Paragraph('Probe ID: %s'%target['probeid'], ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading))
                ]
            else:
                nested[index % 2] = [
                    img,
                    draw,
                    Paragraph('Serial Number: %d'%(index + 1), ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)),
                    Paragraph('Similarity score: %.2f%% (%s)'%(target['sim'], FaceAI.get_similarity_str([], target['sim'], "", 100)), ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading))
                ]
            if ((targets_len % 2 != 0) & (index == targets_len - 1)):
                table = Table([[nested[0]]],
                    colWidths=('50%'),
                    rowHeights=None,
                    style=tablestyle2)
                elements.append(table)
                
            if index % 2 == 0:
                continue
            table = Table([[nested[0], nested[1]]],
                    colWidths=('50%', '50%'),
                    rowHeights=None,
                    style=tablestyle2)
            elements.append(table)

        elements.append(Paragraph('Metadata', ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_CENTER, textColor=black, leading=20, spaceBefore=spacing*2, spaceAfter=spacing)))        
        
        jsondata = json.dumps(reportinfo["json"], indent=4)
        json_parse = jsondata.split('\\n')
        for jdata in json_parse:
            jdata_ = jdata.replace("\\", "")
            tabs = jdata_.split("  ")
            if len(tabs) > 2:
                tab_cnt = len(tabs) - 1
                elements.append(Paragraph("&nbsp;&nbsp;" * tab_cnt + jdata_, ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)))
            else:
                elements.append(Paragraph(jdata_, ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading)))

        elements.append(Paragraph('NB', ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_CENTER, textColor=black, leading=20, spaceBefore=spacing*2, spaceAfter=spacing)))        
        elements.append(Paragraph(Common.PDF_NB_PARA1, ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading, spaceAfter=nb_spacing)))
        elements.append(Paragraph(Common.PDF_NB_PARA2, ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading, spaceAfter=nb_spacing)))
        elements.append(Paragraph(Common.PDF_NB_PARA3, ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading, spaceAfter=nb_spacing)))
        elements.append(Paragraph(Common.PDF_NB_PARA4, ParagraphStyle(name="style", fontName="Arial", fontSize=textsize, alignment=TA_LEFT, textColor=black, leading=leading, spaceAfter=nb_spacing)))

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                  canvasmaker=NumberedCanvas)        

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.logo = r'./images/FaceAI_Logo.png'
        self.pagesize = (8.5 * inch, 14 * inch)
        self.width, self.height = self.pagesize
        self.margin_x = 0.4 * inch
        self.margin_y = 0.5 * inch
        self._saved_page_states = []
 

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
 

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
 
    def draw_page_number(self, page_count):
        self.drawImage(self.logo, 26, self.height - 50, width=80, height=47, mask='auto')
        self.saveState()
        self.setStrokeColor(HexColor(0x0070C0))
        self.setLineWidth(0.5)
        # self.drawImage(self.logo, self.width-inch*8-5, self.height-50, width=100, height=20, preserveAspectRatio=True)
        self.line(30, self.height - self.margin_y * 1.6, LETTER[0] - 50, self.height - self.margin_y * 1.6)
        self.restoreState()
        self.setFont("Arial", 12)
        self.drawRightString(self.width / 2.0 + 10, 0.35 * inch,
                             "Page %d of %d" % (self._pageNumber, page_count))


def gen_pdf_filename(probe_id, case_num, ps):
    return 'probe_report_%s_%s_%s'%(probe_id, case_num, ps)

def create_pdf(probe_id, probe_result, file_location):   
    systime = SysTimer.now()   
    ntptime = ntp_get_time_from_object(systime) 
    try:
        buffer = BytesIO()
        repo_desc = ''
        if probe_result.matched == 'Matched':
            if probe_result.case_info.target_type == 1:
                repo_desc = Common.REPORT_DESCRIPTION_MATCHED_FOR_SINGLE
            elif probe_result.case_info.target_type == 2:
                repo_desc = Common.REPORT_DESCRIPTION_MATCHED_FOR_MULTIPLE
            elif probe_result.case_info.target_type == 3:
                repo_desc = Common.REPORT_DESCRIPTION_MATCHED_FOR_ENTIRE
            elif probe_result.case_info.target_type == 4:
                repo_desc = Common.REPORT_DESCRIPTION_MATCHED_FOR_OLDCASE
        else:
            repo_desc = Common.REPORT_DESCRIPTION_NON_MATCHED

        reportinfo = {
            "subject": probe_result.case_info.subject_image_url,
            "result": probe_result.matched,
            "created": datetime.strftime(ntptime, "%d/%m/%Y %I:%M %p"),
            "casenum": probe_result.case_info.case_number,
            "ps": probe_result.case_info.case_PS,
            "description": repo_desc,
            "examname": probe_result.case_info.examiner_name,
            "examnum": probe_result.case_info.examiner_no,
            "remarks": probe_result.case_info.remarks,
            "json": Common.convert_json_for_page(probe_result)
        }

        reportinfo["targets"] = []
        if probe_result.case_info.is_used_old_cases:
            db = DBConnection()
            old_case_data_for_results = db.get_case_data(probe_result.json_result['results'])

        for index, result in enumerate(probe_result.json_result['results']):
            conf_buff = result['confidence'][:len(result['confidence']) - 1]
            if probe_result.case_info.is_used_old_cases:
                reportinfo["targets"].append({
                    "path": result["image_path"],
                    "sim": float(conf_buff),
                    "oldcase": probe_result.case_info.is_used_old_cases,
                    "caseno": old_case_data_for_results[index][0],
                    "ps": old_case_data_for_results[index][1],
                    "probeid": old_case_data_for_results[index][2],
                    "face_rect": probe_result.json_result['faces'][index]['face_rectangle']
                })
            else:
                reportinfo["targets"].append({
                    "path": result["image_path"],
                    "sim": float(conf_buff),
                    "oldcase": probe_result.case_info.is_used_old_cases,
                    "face_rect": probe_result.json_result['faces'][index]['face_rectangle']
                })
            

        report = GenReport(buffer, probe_id)
        pdf = report.print_reports(reportinfo)
        buffer.seek(0)
    
        with open(file_location, 'wb') as f:
            f.write(buffer.read())

        return True
    except Exception as e:
        print(e)
        return False

def export_report_pdf(file_path, ex_file_name, file_name):    
    report_path = Common.get_reg(Common.REG_KEY)
    if report_path:
        report_path = report_path + "/" + Common.REPORTS_PATH
    else:
        report_path = Common.STORAGE_PATH + "/" + Common.REPORTS_PATH        
    Common.create_path(report_path)  
    
    try:
        decrypt_file_to(os.path.join(report_path, ex_file_name), os.path.join(file_path, file_name+".pdf"))
    except Exception as e:
        print("export_report_pdf: ", e)
        return False

    return True
    

    