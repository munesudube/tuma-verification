import cv2
from deepface import DeepFace
import pytesseract

image = cv2.imread( "image2.jpeg" )
text = pytesseract.image_to_string( cv2.cvtColor( image, cv2.COLOR_BGR2GRAY ) )
print( text )

result = DeepFace.verify( "image1.jpeg", "image2.jpeg" )
print( result )