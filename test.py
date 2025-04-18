from PIL import Image, ExifTags
import os
from deepface import DeepFace
import numpy as np
import tempfile
import cv2

def crop_face( img_path ):
    img = cv2.imread(img_path)

    # detect face
    faces = DeepFace.extract_faces(img_path, enforce_detection=False)

    # crop and save first face
    if faces:
        face = faces[0]['facial_area']
        x, y, w, h = face['x'], face['y'], face['w'], face['h']
        face_img = img[y:y+h, x:x+w]
        face_img = cv2.resize(face_img, (224, 224))  # optimal for most models
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        print( temp_file.name )
        cv2.imwrite( temp_file.name , face_img)
        return temp_file.name
        

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



def debug_exif_data( image_path ):
    try:
        img = Image.open( image_path )
        exif_data = img._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get( tag, tag )
                if( tag_name == "UserComment" ):
                    pass
                else:
                    print( f"{tag_name}: {value}" )
    except Exception as e:
        print( f"Error reading EXIF data: {str(e)}" )
        
def has_necessary_exif(image_path):
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
    
def doVerify( img1, img2 ):
    img1 = prepare_image_for_deepface( img1 )
    img2 = prepare_image_for_deepface( img2 )
    
    #img1 = crop_face( img1 )
    #img2 = crop_face( img2 )
    if not all( img is not None for img in [img1, img2] ):
        print( "Verification halted" )
        return
    #print( img1 )
    #print( img2 )
    return DeepFace.verify( img1, img2, enforce_detection = False )

def test():
    img1 = os.path.abspath( "images/53b82714-39e5-47fe-bd19-63ab7ae43993.jpg" )
    img2 = os.path.abspath( "images/532867dc-fd6a-404a-8a90-230ababd4d74.jpg" )
    img3 = os.path.abspath( "images/0401a5d3-e89f-45c4-832d-0bb32723ee71.jpg" )
    #result = DeepFace.verify( img1, img2)
    #print(result)
    
    for img in [img2, img3]:
        if not has_necessary_exif( img ):
            print( f"{ img } has missing metadata" )
            return
    print( "All images are good" )
    
    result = doVerify( img2, img3 )
    print( result )
    


test()

