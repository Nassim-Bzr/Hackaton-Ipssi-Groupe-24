# preprocess.py   fichier de service pour préparer l'image avant la lecture OCR (nettoyage, redressement)
import cv2                              
import numpy as np                      
from pdf2image import convert_from_path 




# Convertion de la première page du PDF en image utilisable par OpenCV
def pdf_vers_image(chemin_pdf):
    
    pages = convert_from_path(chemin_pdf, dpi=300)  
    premiere_page = pages[0]                         
    image = np.array(premiere_page)                  
    return image                                    



# Convertion de  l'image couleur en niveaux de gris 
def en_niveaux_de_gris(image):
    gris = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  
    return gris                             




# Redressement de l'image si elle est inclinée 
def redresser(image):
    coords = np.column_stack(np.where(image > 0))    # Trouve les coordonnées des pixels non noirs 
    angle = cv2.minAreaRect(coords)[-1]             
    if angle < -45:                                  
        angle = -(90 + angle)
    else:
        angle = -angle                               
    h, w = image.shape[:2]                           
    centre = (w // 2, h // 2)                        
    matrice = cv2.getRotationMatrix2D(centre, angle, 1.0)  
    redressee = cv2.warpAffine(image, matrice, (w, h))    
    return redressee                                        



 # Fonction principale : enchaîne toutes les étapes de préparation de l'image
def preprocess(chemin_fichier):
   

    if chemin_fichier.endswith(".pdf"):              
        image = pdf_vers_image(chemin_fichier)      
    else:                                            
        image = cv2.imread(chemin_fichier)           
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  

    image = en_niveaux_de_gris(image)  
    image = redresser(image)           
    return image                       # image propre prête pour l'OCR
