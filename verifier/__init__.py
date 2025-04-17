import cv2
import os
from deepface import DeepFace
import numpy as np
import easyocr
import importlib
import urllib.request
import uuid
from PIL import Image, ExifTags

ocrReader = easyocr.Reader(['en'], gpu=False, verbose=False)

def fix_orientation(image_path):
    image = Image.open(image_path)

    try:
        exif = image._getexif()
        if exif is not None:
            # Find the orientation tag (usually 274)
            for tag, value in ExifTags.TAGS.items():
                if value == 'Orientation':
                    orientation_tag = tag
                    break

            orientation = exif.get(orientation_tag)

            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
    except Exception as e:
        print("Orientation correction failed:", e)

    return image


def getFileExtensionFromUrl( url ):
    return url.split( "." )[-1]

def download_image(url):
    if not url:
        return False
    filename = os.path.join( "images", generateRandomFileName( getFileExtensionFromUrl( url ) ) )
    filename = os.path.abspath( filename )
    try:
        urllib.request.urlretrieve(url, filename)
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            image = fix_orientation( filename )
            image.save( filename )
            return filename
        else:
            return False
    except Exception:
        return False

def saveFaceImage( image, filePath ):
    dirname = os.path.dirname( filePath )
    filename = "face-" + os.path.splitext(os.path.basename(filePath))[0]
    filePath = os.path.join( dirname, filename + ".jpg" )
    print( filePath )
    cv2.imwrite( filePath, image )

def generateRandomFileName( extension ):
    return f"{uuid.uuid4()}.{extension}"

def deleteFile( path ):
    if os.path.exists( path ):
        os.remove( path )


class Verifier:
    def defaultResult( self ):
        return { 
            "idInfo": {}, 
            "validId": False,
            "validIdImage": False,
            "verifiedId": False,
            "validSelfie": False,
            "verifiedSelfie": False,
            "extractedText": "",
            "verified": False,
            "message": "",
            "signature": "tuma-verification-1.0.0",
            "version": "1.0.0",
            "confidence": "",
            "country": "Unknown"
        }

    def validateSelfie( self, selfieUri ):
        result = { "valid": False, "message": "" }
        selfiePath = download_image( selfieUri )
        if not selfiePath:
            result["message"] = "Selfie file does not exist"
            return result

        face = self.detectFace( selfiePath )
        if face is None:
            result["message"] = "Face not detected on selfie"
            deleteFile( selfiePath )
            return result

        result["valid"] = True
        result["message"] = "Valid"
        deleteFile( selfiePath )
        return result

    def extractData( self, idImageUri, countryCode, docType ):
        result = { "success": False, "message": "", "data": None }
        idImagePath = download_image( idImageUri )
        if not idImagePath:
            result["message"] = "ID image file does not exist"
            return result

        textData = self.extractText( idImagePath )
        deleteFile( idImagePath )

        if not textData:
            result["message"] = "No text extracted from ID image"
            return result

        module_name = f"verifier.countries.{ countryCode.lower() }"
        try:
            country_module = importlib.import_module(module_name)
            _verifier = country_module.Verifier()
            _result = _verifier.extractData( textData, docType )
            result["data"] = _result
        except ModuleNotFoundError:
            pass
        
        result["success"] = True
        result["message"] = "Data extracted successfully"        
        return result

    def verify( self, idImageUri, selfieUri ):
        result = { "verified": False, "message": "" }
        idImagePath = download_image( idImageUri )
        selfiePath = download_image( selfieUri )
        if not idImagePath or not selfiePath:
            result["message"] = "ID or selfie file does not exist"
            deleteFile( idImagePath )
            deleteFile( selfiePath )
            return result

        face = self.detectFace( selfiePath )
        if face is None:
            result["message"] = "Face not detected on selfie"
            deleteFile( idImagePath )
            deleteFile( selfiePath )
            return result

        idFace = self.detectFace( idImagePath )
        if idFace is None:
            result["message"] = "Face not detected on ID"
            deleteFile( idImagePath )
            deleteFile( selfiePath )
            return result

        #saveFaceImage( idFace, idImagePath )
        #saveFaceImage( face, selfiePath )

        try:
            result["verified"] = DeepFace.verify( idImagePath, selfiePath )["verified"]
        except Exception as e:
            deleteFile( idImagePath )
            deleteFile( selfiePath )
            result["message"] = "Face not detected on ID. Make sure it is clear/upright"
            return result

        deleteFile( idImagePath )
        deleteFile( selfiePath )
        result["message"] = "Selfie matches ID" if result["verified"] else "Selfie does not match ID Image"
        return result


    def _verify( self, data ):
        result = self.defaultResult()
        result["data"] = data

        countryCode = data.get( "countryCode")

        idImagePath = download_image( data.get( "idImage" ) )
        selfiePath = download_image( data.get( "selfie" ) )

        if not countryCode or not idImagePath or not selfiePath:
            missing = []
            if not countryCode: missing.append( "Country" )
            if not idImagePath: missing.append( "ID" )
            if not selfiePath: missing.append( "Selfie" )
            
            result["message"] = f"Missing information ( { ', '.join( missing ) } )"
            return result

        if not os.path.exists( idImagePath ) or not os.path.exists( selfiePath ):
            result["message"] = "ID or selfie file does not exist"
            return result

        textData = self.extractText( idImagePath )

        result["extractedText"] = "\n".join( textData )

        
        module_name = f"verifier.countries.{ countryCode.lower() }"
        try:
            country_module = importlib.import_module(module_name)
            _verifier = country_module.Verifier()
            _result = _verifier.verify( textData, data )
            _result["country"] = _verifier.name
            result.update( _result )
        except ModuleNotFoundError:
            pass

        if not result["validId"] or not result["verifiedId"]:
            return result

        idFace = self.detectFace( idImagePath )
        selfieFace = self.detectFace( selfiePath )

        saveFaceImage( idFace, idImagePath )
        saveFaceImage( selfieFace, selfiePath )
        
        if idFace is None:
            result["message"] = "Face not detected on ID"
            return result
        else:
            result["validIdImage"] = True

        if selfieFace is None:
            result["message"] = "Face not detected on selfie"
            return result
        else:
            result["validSelfie"] = True 

        result["verifiedSelfie"] = DeepFace.verify( idImagePath, selfiePath )["verified"]

        result["confidence"] = ""
        if not result["verifiedSelfie"]:
            result["message"] = "Selfie does not match ID"
            return result

        result["message"] = "All good"            
        result["verified"] = result["validId"] and result["validIdImage"] and result["verifiedId"] and result["validSelfie"] and result["verifiedSelfie"]
        
        return result

    def extractText( self, imagePath ):        
        if not imagePath or not os.path.exists( imagePath ):
            return ""
        image = cv2.imread( imagePath )
        gray = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY )
        text = ocrReader.readtext( gray, detail=0 )
        return text
        

    def detectFace( self, imagePath ):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        image = cv2.imread( imagePath )
        gray = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY )
        
        faces = face_cascade.detectMultiScale( gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30) )
        
        if len(faces) == 0:
            return None  # No face detected
        
        x, y, w, h = faces[0]  # Get the first detected face
        return image[y:y+h, x:x+w]  # Crop the face region