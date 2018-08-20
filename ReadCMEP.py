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

badMappings=[]
mappingDict={}

with open('mapping.json','r') as fp:
    for line in fp:
        tempDict=json.loads(line.strip())
        mappingDict[(tempDict['X'],tempDict['Y'],tempDict['Page'])]=tempDict['Field']

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
                if boundingBox in mappingDict:
                    temp=mappingDict[boundingBox]
                    valuesDict[temp]=lt_obj.get_text().strip()
        for key in mappingDict:
            if key[2]==currentPage:
                temp=mappingDict[key]
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
    worksheet.write(row, 0, 'Key')
    worksheet.write(row, 1, 'Value')
    for key in valuesDict:
        row+=1
        worksheet.write(row, 0, key)
        worksheet.write(row, 1, valuesDict[key])
    workbook.close

    #print(file,valuesDict)
