import cv2
import os
from deepface import DeepFace
import numpy as np
import easyocr
import importlib
import urllib.request
import uuid
from PIL import Image
import numpy as np
from PIL import Image, ExifTags

ocrReader = easyocr.Reader(['en'], gpu=False, verbose=False)

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
            return filename
        else:
            return False
    except Exception:
        return False
    
def prepare_image_for_deepface(image_path):
    try:
        image = Image.open(image_path)

        # --- Fix orientation ---
        """try:
            exif = image._getexif()
            if exif:
                orientation_key = next(
                    (key for key, val in ExifTags.TAGS.items() if val == 'Orientation'),
                    None
                )
                if orientation_key and orientation_key in exif:
                    orientation = exif[orientation_key]
                    if orientation == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)
        except Exception as e:
            print("Orientation fix skipped:", e)"""
        
        if image.width > 1600 or image.height > 1600: 
            #pass
            #print( f"Width: { image.width }, Height: { image.height }" )
            val = max( max( image.width, image.height ) // 3, 800 )
            #print( f"MAX VALUE = { val }" )
            image.thumbnail((val, val))  # Keeps face detail
            #print( f"Width: { image.width }, Height: { image.height }" )
            #image.thumbnail( (3500, 3500), Image.Resampling.LANCZOS )  # Keeps face detail

        # --- Resize if needed ---
        #image.thumbnail(max_size)

        # --- Convert to RGB ---
        image = image.convert("RGB")

        #temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        #image.save(temp_file.name, format="JPEG")
        #return temp_file.name
        return np.array(image)

    except Exception as e:
        print("Failed to prepare image:", e)
        return None

def generateRandomFileName( extension ):
    return f"{uuid.uuid4()}.{extension}"

def deleteFile( path ):
    if (path is not None) and os.path.exists( path ) and False:
        os.remove( path )
        
def has_necessary_exif( image_path ):
    try:
        image = Image.open(image_path)
        exif = image._getexif()
        if not exif:
            return False

        exif_data = {ExifTags.TAGS.get(tag): value for tag, value in exif.items() if tag in ExifTags.TAGS}

        required_tags = ["ImageWidth", "ImageLength", "Orientation"]
        return all(tag in exif_data for tag in required_tags)
    except Exception as e:
        print("Error reading EXIF:", e)
        return False

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

        for img in [selfiePath, idImagePath]:
            if not has_necessary_exif( img ):
                imgType = "selfie" if img == selfiePath else "id"
                result["message"] = f"Ensure { imgType } image was taken by your camera"
                return result

        try:
            #idImage = prepare_image( idImagePath )
            #selfie = prepare_image( selfiePath )
            idImage = prepare_image_for_deepface( idImagePath )
            selfie = prepare_image_for_deepface( selfiePath )
            result["verified"] = DeepFace.verify( idImage, selfie, enforce_detection = False )["verified"]
        except Exception as e:
            print( "MUNESU ---->", e )
            print( idImagePath )
            print( selfiePath )
            deleteFile( idImagePath )
            deleteFile( selfiePath )
            result["message"] = "Face not detected on ID/Selfie. Make sure they are both clear/upright"
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