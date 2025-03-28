import easyocr
import os
import cv2
from verifier.countries.ca import Verifier


def extractData( image_path, reader, userData ):
    image_path = os.path.abspath( image_path )
    image = cv2.imread(image_path)
    gray = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY )

    if image is None:
        print("Error: Could not load image. Check the file path!")
    else:        
        text = reader.readtext( gray, detail=0 )
        for t in text:
            print( t )
        verifier = Verifier()
        result = verifier.verify( text, userData ) #Driver's License
        print( result["idInfo"] )

reader = easyocr.Reader(['en'], gpu=False)
for item in [
    {"path": "philong.jpeg", "docType": "DL"}, 
    {"path": "brenda.jpeg", "docType": "DL"}
    ]:
    print( "\n" )
    print( item["path"] )
    extractData( item["path"], reader, item )


