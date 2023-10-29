import cv2
import numpy as np
from PIL import Image
import os

# Path for face image database
path = 'user/database'

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

# function to get the images and label data
def getImagesAndLabels(path):

    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []
    for imagePath in imagePaths:

        for image in os.listdir(imagePath):
            img_path = os.path.join(imagePath, image)
            PIL_img = Image.open(img_path).convert('L') # convert it to grayscale
            img_numpy = np.array(PIL_img,'uint8')

            id = int(imagePath.split("/")[-1])
            faces = detector.detectMultiScale(img_numpy)

            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)

    return faceSamples,ids

print ("\nTraining faces. It will take a few seconds. Wait ...")
faces,ids = getImagesAndLabels(path)

recognizer.train(faces, np.array(ids))

# Save the model into trainer/trainer.yml
recognizer.save('trainer/trainer.yml') 

print("\n{0} faces trained. Exiting Program".format(len(np.unique(ids))))