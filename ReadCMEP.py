from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTFigure, LTTextBox, LTTextLine, LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import os
import sys
import json

badMappings=[]
mappingDict={}

#mappingDict[(127.25, 679.63)]="RequisitionID"
##mappingDict[(126.0, 663.38)]="PatientName"
#mappingDict[(126.65, 643.38)]="PatientAge"
#mappingDict[(128.65, 626.33)]="PatientSex"
"""mappingDict[(127.25,679.63)]='Requisition'
mappingDict[(126.0,663.38)]='Name'
mappingDict[(126.65,643.38)]='Age'
mappingDict[(128.65,626.33)]='Sex'
mappingDict[(438.0,679.63)]='Physician'
mappingDict[(438.0,663.13)]='DateOfCollection'
mappingDict[(438.0,643.38)]='TimeOfCollection'
mappingDict[(438.0,626.33)]='PrintDate'
mappingDict[(298.9,505.45)]='Citramalic'
mappingDict[(298.9,484.7)]='5-Hydroxymethyl-2-furoic'
mappingDict[(298.9,463.95)]='3-Oxoglutaric'
mappingDict[(298.9,443.2)]='Furan-2,5-dicarboxylic'
mappingDict[(298.9,422.45)]='Furancarbonylglycine'
mappingDict[(298.9,401.7)]='Tartaric'
mappingDict[(298.9,380.95)]='Arabinose'
mappingDict[(298.9,360.2)]='Carboxycitric'
mappingDict[(298.9,339.45)]='Tricarballylic'
mappingDict[(298.9,307.05)]='Hippuric'
mappingDict[(298.9,286.3)]='2-Hydroxyphenylacetic'
mappingDict[(298.9,265.55)]='4-Hydroxybenzoic'
mappingDict[(298.9,244.8)]='4-Hydroxyhippuric'
mappingDict[(298.9,224.05)]='DHPPA'
mappingDict[(298.9,191.65)]='4-Hydroxyphenylacetic'
mappingDict[(298.9,170.9)]='HPHPA'
mappingDict[(298.9,150.15)]='4-Cresol'
mappingDict[(298.9,129.4)]='3-Indoleacetic'
"""
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

    fp.close()
    with open('output/'+file.replace("pdf","txt"),'w') as output_file:
        for key in valuesDict:
            output_file.write(key+": "+valuesDict[key]+'\n')
    #print(file,valuesDict)
