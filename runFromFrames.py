"""
Emotion Recognition - Frame-Based Face Channel

__author__ = "Pablo Barros"

__version__ = "0.1"
__maintainer__ = "Pablo Barros"
__email__ = "barros@informatik.uni-hamburg.de"

More information about the implementation of the model:

Barros, P., Churamani, N., & Sciutti, A. (2020). The FaceChannel: A Light-weight Deep Neural Network for Facial Expression Recognition. arXiv preprint arXiv:2004.08195.

Barros, P., & Wermter, S. (2016). Developing crossmodal expression recognition based on a deep neural model. Adaptive behavior, 24(5), 373-396.
http://journals.sagepub.com/doi/full/10.1177/1059712316664017

"""

import numpy
import cv2
from Utils import imageProcessingUtil, modelDictionary, modelLoader, GUIController
import os
import time

import csv

import tensorflow as tf
config = tf.ConfigProto()
config.gpu_options.allow_growth=True
sess = tf.Session(config=config)


"""Directories"""
loadFramesFrom = "/home/pablo/Documents/Datasets/testFC/frames" #Folde where the videos are
saveCSVFiles = "/home/pablo/Documents/Datasets/testFC/file" #Folder that will hold the .csv files
saveNewFrames = "/home/pablo/Documents/Datasets/testFC/newFrames" #Folder that will hold the .csv files

"""Auxiliary parameters"""
filesFormat = [".ppm", ".png"]
finalImageSize = (1024,768) # Size of the final image generated by the demo


"""Demo Variables"""
modelDimensional = modelLoader.modelLoader(modelDictionary.DimensionalModel) #Load neural network

imageProcessing = imageProcessingUtil.imageProcessingUtil()

GUIController = GUIController.GUIController()

arousals = []
valences = []


"""
Opens the .csv file 
"""
with open(saveCSVFiles+".csv", mode='a') as employee_file:
    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    employee_writer.writerow(['Frame', 'Arousal', 'Valence'])

    dataList = os.listdir(loadFramesFrom)
    newDataList = []
    for a in dataList:
        addNew = False
        for format in filesFormat:
            if format in a:
                addNew = True
        if addNew:
            newDataList.append(a)


    dataList = newDataList
    dataList = sorted(dataList, key=lambda x: int(x.split(".")[0]))


    for frameName in dataList:  # for each frame inside this folder
        print ("Started Frame:" + str(loadFramesFrom + "/" + frameName))

        frameDirectory = str(loadFramesFrom + "/" + frameName)
        frame = cv2.imread(loadFramesFrom + "/" + frameName)

        frame = cv2.resize(frame, (640, 480))
        facePoints, face = imageProcessing.detectFace(frame) #detect a face

        # create display image and copy the captured frame to it

        image = numpy.zeros((finalImageSize[1], finalImageSize[0], 3), numpy.uint8)
        image[0:480, 0:640] = frame
        frame = image


        if not len(face) == 0:   # If a face is detected

            face = imageProcessing.preProcess(face,imageSize=(64,64))     # pre-process the face

            dimensionalRecognition = numpy.array(modelDimensional.classify(face))    # Obtain dimensional classification

            # Print the square around the categorical face
            frame = GUIController.createDetectedFacGUI(frame, facePoints,
                                                       modelDictionary=[],
                                                       categoricalClassificationReport=[])
            # Create the dimensional graph
            frame = GUIController.createDimensionalEmotionGUI(dimensionalRecognition, frame, categoricalReport=[],
                                                              categoricalDictionary=None)

            #Create dimensional plot
            arousals.append(dimensionalRecognition[0][0][0])
            valences.append(dimensionalRecognition[1][0][0])
            if len(arousals) > 100:
                arousals.pop(0)
                valences.pop(0)

            frame = GUIController.createDimensionalPlotGUI(arousals, valences, frame)

            cv2.imwrite(saveNewFrames+"/"+frameName, frame)
        else: #if there is no face
            dimensionalRecognition = [-99,-99]
        # print ("DImensional: " + str(dimensionalRecognition))
        employee_writer.writerow([frameDirectory, dimensionalRecognition[0][0][0], dimensionalRecognition[1][0][0]])
        # print("-- Frame: " + str(frameCount))
        # print("FPS: ", 1.0 / (time.time() - start_time))  # FPS = 1 / time to process loop


    cv2.destroyAllWindows()