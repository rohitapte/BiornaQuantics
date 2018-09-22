import os

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfdocument import PDFDocument, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

basepath='GI-MAP/'
#basepath='Complete Metabolic Energy Profile/'
filename='GIMAPZ_Michelle Saddington_2018.07.30.pdf'
#filename='FoodS_Abi Tyrrell_2016.06.02.pdf'
#filename='CMEP_Aditya Baddrinath_2018.01.29.pdf'
files=[file for file in os.listdir(basepath)]
#print(files)
#filename=files[2]
print(filename)
file=os.path.join(basepath+filename)

password=''
extracted_text =''

fp = open(file, "rb")
parser = PDFParser(fp)
document = PDFDocument(parser, password)

# Check if document is extractable, if not abort
if not document.is_extractable:
	raise PDFTextExtractionNotAllowed

# Create PDFResourceManager object that stores shared resources such as fonts or images
rsrcmgr=PDFResourceManager()

# set parameters for analysis
laparams=LAParams()

# Create a PDFDevice object which translates interpreted information into desired format
# Device needs to be connected to resource manager to store shared resources
# device = PDFDevice(rsrcmgr)
# Extract the decive to page aggregator to get LT object elements
device=PDFPageAggregator(rsrcmgr, laparams=laparams)

# Create interpreter object to process page content from PDFDocument
# Interpreter needs to be connected to resource manager for shared resources and device
interpreter=PDFPageInterpreter(rsrcmgr, device)
pageCount=0

# Ok now that we have everything to process a pdf document, lets process it page by page
pages=PDFPage.create_pages(document)
for page in pages:
    pageCount+=1
    if pageCount==2:
        # As the interpreter processes the page stored in PDFDocument object
        interpreter.process_page(page)
        # The device renders the layout from interpreter
        layout = device.get_result()
        # Out of the many LT objects within layout, we are interested in LTTextBox and LTTextLine
        for lt_obj in layout:
            if lt_obj.__class__.__name__ == "LTTextBoxHorizontal":
                boundingBox = (round(lt_obj.bbox[0], 2), round(lt_obj.bbox[1], 2))
                temp=lt_obj.get_text().strip()
                if len(temp)>0:
                    print(temp,boundingBox,lt_obj.bbox[2],lt_obj.bbox[3])
                    #print('{"Field":'+temp+',"X":'+str(boundingBox[0])+',"Y":'+str(boundingBox[1])+'}')
        break
# close the pdf file
fp.close()

