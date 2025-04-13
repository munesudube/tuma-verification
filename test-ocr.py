import easyocr
import os
import cv2
from verifier.countries.ca import Verifier


def extractData( image_path, docType, reader ):
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
        result = verifier.extractData( text, docType )
        print( result )

reader = easyocr.Reader(['en'], gpu=False)
for item in [
        #{"path": "philong.jpeg", "docType": "DL"}, 
        #{"path": "brenda.jpeg", "docType": "DL"},
        {"path": "examples/Hope Mwebaze-Passport.jpeg", "docType": "PP"},
        #{"path": "examples/Batanda Ziwa Mohamed - PermResCard.jpeg", "docType": "PRC"},
    ]:
    print( "\n" )
    print( item["path"] )
    extractData( item["path"], item['docType'], reader )


