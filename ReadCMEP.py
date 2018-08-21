from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTFigure, LTTextBox, LTTextLine, LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import os
import sys
import json
import xlsxwriter
from datetime import datetime
pdfMappingDict={}
with open('pdf_mapping.json','r') as fp:
    for line in fp:
        tempDict=json.loads(line.strip())
        pdfMappingDict[(tempDict['X'],tempDict['Y'],tempDict['Page'])]=tempDict['Field']

labToInternalMappingDict={}
with open('lab_to_internal_mapping.json') as fp:
    for line in fp:
        tempDict=json.loads(line.strip())
        labToInternalMappingDict[tempDict['LabName']]=tempDict['InternalName']

files=os.listdir('Complete Metabolic Energy Profile/')
files=[file for file in files if 'pdf' in file]
#files=files[:10]
#files=['CMEP_Anthony Dixon 2018.05.21.pdf']
for file in files:
    valuesDict = {}
    fp=open('Complete Metabolic Energy Profile/'+file,'rb')
    parser=PDFParser(fp)
    doc=PDFDocument(parser)

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    currentPage=0
    for page in PDFPage.create_pages(doc):
        currentPage+=1
        interpreter.process_page(page)
        layout = device.get_result()
        for lt_obj in layout:
            if lt_obj.__class__.__name__=="LTTextBoxHorizontal":
                boundingBox=(round(lt_obj.bbox[0],2),round(lt_obj.bbox[1],2),currentPage)
                if boundingBox in pdfMappingDict:
                    temp=pdfMappingDict[boundingBox]
                    valuesDict[temp]=lt_obj.get_text().strip()

        for key in pdfMappingDict:
            if key[2]==currentPage:
                temp=pdfMappingDict[key]
                if temp not in valuesDict:
                    valuesDict[temp]=""
                    min_dist = sys.float_info.max
                    for lt_obj in layout:
                        # find the closest one
                        boundingBox = (round(lt_obj.bbox[0], 2), round(lt_obj.bbox[1], 2))
                        dist = (boundingBox[0] - key[0]) ** 2 + (boundingBox[1] - key[1]) ** 2
                        if dist < min_dist:
                            min_dist = dist
                            valuesDict[temp]=lt_obj.get_text().strip()
                    if min_dist>20:
                        print("Exact marker location not found for " + file + " field " + temp + ". Using nearest distance "+str(min_dist))

    fp.close()
    with open('output/'+file.replace("pdf","txt"),'w') as output_file:
        for key in valuesDict:
            output_file.write(key+": "+valuesDict[key]+'\n')
    workbook = xlsxwriter.Workbook('exceloutput/'+file.replace("pdf","xls"))
    worksheet = workbook.add_worksheet('measurements')
    row=0
    worksheet.write(row, 0, 'LabMarker')
    worksheet.write(row, 1, 'InternalMarker')
    worksheet.write(row, 2, 'Value')
    worksheet.write(row, 3, 'MeasuredAt')
    sMeasuredAt=valuesDict['DateOfCollection']
    if len(sMeasuredAt)==9:
        sMeasuredAt='0'+sMeasuredAt
    sTime=valuesDict['TimeOfCollection']
    if sTime=='00:00 AM':
        sTime='12:00 AM'
    sMeasuredAt=sMeasuredAt+' '+sTime
    sDateDisplay=''
    try:
        measuredDate = datetime.strptime(sMeasuredAt, '%m/%d/%Y %I:%M %p')
        sDateDisplay=measuredDate.isoformat()+'.000Z'
    except ValueError:
        print("Incorrect Date format for "+valuesDict['Name'])
    for key in valuesDict:
        if key not in ['Requisition','Name','Age','Sex','Physician','DateOfCollection','TimeOfCollection','PrintDate']:
            row+=1
            worksheet.write(row, 0, key)
            worksheet.write(row, 1, labToInternalMappingDict[key])
            worksheet.write(row, 2, valuesDict[key])
            worksheet.write(row, 3,sDateDisplay)
    workbook.close()


    #print(file,valuesDict)
