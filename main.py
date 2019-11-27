import os
import urllib.request
# from recordingPipeline import *
import IPython.display as ipd
import pandas as pd
import numpy as np
import librosa
import librosa.display
import glob
from pydub import AudioSegment
import wave
import sys
import scipy.io.wavfile
from xgboost import XGBClassifier
import pickle
from flask_app import app
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import soundfile as sf
import io
import os, shutil
from sklearn.svm import SVC
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence
from keras.optimizers import RMSprop
from keras.models import load_model
from keras import backend as K


@app.route('/')               
def index():
	return render_template('index.html') 

@app.route('/save-record', methods=['POST'])
def save_record():  
    K.clear_session()
    a = request.files['file'].read()  
    return spokenIdentifier(a)

def clean_folder():
    folder = './static/wavSplittedFiles'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    return

def spokenIdentifier(audiofromclient):

    #Splitting the file
    s = io.BytesIO(audiofromclient)
    newAudio = AudioSegment.from_file(s)
    #newAudio=audiofromclient
    
    clean_folder()   
    print("Hello->1")
    n=round(len(newAudio)/10000)
    for i in range(n):
        m=i*10000
        splitAudio=newAudio[m:m+10000]
        path11='./static/wavSplittedFiles/file' + str(i) +'.wav'
        splitAudio.export(path11, format="wav")
          
    
    #Loading all files and extracting the features
    path = './static/WavSplittedFiles/' 
    print("Hello->2")
    files = os.listdir(path)

    X_Features=[]


    for name in files:
        file_name=os.path.join(os.path.abspath(path), name)
   
         # handle exception to check if there isn't a file which is corrupted
        try:
         # here kaiser_fast is a technique used for faster extraction
         X, sample_rate = librosa.load(file_name, res_type='kaiser_fast') 
         # we extract mfcc feature from data
         mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T,axis=0) 
        except Exception as e:
             print("Error encountered while parsing file: ", name)
        
        feature=mfccs
        X_Features.append(feature)

    print("Hello->3")
     #Updating X for model input
    X_Features=pd.DataFrame(X_Features)
    X_Features.columns=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
        '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22',
        '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34',
        '35', '36', '37', '38', '39']

    print("Hello->4")
    print(X_Features)
    #filename2= "./models/model_XGB_MixData.sav"
    #loaded_model_XGB=pickle.load(open(filename2,'rb'))
    #y_pred=loaded_model_XGB.predict(X_Features)
    #print("Hello->5")
    #print(y_pred)
    finalPred=ensembling_1(X_Features)
    print(finalPred)
    return finalPred
	#return 

def ensembling_1(X_Features):
    
    predList=[]
    
#    filename2= "./models/ModelSVM_WOM.sav"
#    loaded_model_XGB=pickle.load(open(filename2,'rb'))
#    y_pred=loaded_model_XGB.predict(X_Features)
#    predList.append(y_pred)
#    
#    filename2= "./models/model_XGB.sav"
#    loaded_model_XGB=pickle.load(open(filename2,'rb'))
#    y_pred=loaded_model_XGB.predict(X_Features)
#    predList.append(y_pred) 
#    
#    filename2= "./models/model_XGB_WOM.sav"
#    loaded_model_XGB=pickle.load(open(filename2,'rb'))
#    y_pred=loaded_model_XGB.predict(X_Features)
#    predList.append(y_pred) 
#    
#    
#    filename2= "./models/model_XGB_MixData1125.sav"
#    loaded_model_XGB=pickle.load(open(filename2,'rb'))
#    y_pred=loaded_model_XGB.predict(X_Features)
#    predList.append(y_pred) 
#   
#    filename2= "./models/model_XGB_MixData.sav"
#    loaded_model_XGB=pickle.load(open(filename2,'rb'))
#    y_pred=loaded_model_XGB.predict(X_Features)
#    predList.append(y_pred) 
    
#    filename2= "./models/model_lstm.hdf5"
#    loaded_model_LSTM = load_model(filename2)
    X_Features=np.array(X_Features).reshape(X_Features.shape[0], X_Features.shape[1],1)
#    y_pred=loaded_model_LSTM.predict(X_Features)
#    y_pred1=[]
#    for x in y_pred:
#        if x>=0.5:
#            y_pred1.append(1)
#        else:
#            y_pred1.append(0)
#    predList.append(y_pred1)
    
    filename2= "./models/model_lstm_multi.hdf5"
    loaded_model_LSTM = load_model(filename2)
    y_pred=loaded_model_LSTM.predict(X_Features)
    y_pred1=[]
    for x in y_pred:
        if x>=0.5:
            y_pred1.append(1)
        else:
            y_pred1.append(0)
    predList.append(y_pred1)
    
    
    filename2= "./models/model_lstm_multiStack1125.hdf5"
    loaded_model_LSTM = load_model(filename2)
    y_pred=loaded_model_LSTM.predict(X_Features)
    y_pred1=[]
    for x in y_pred:
        if x>=0.5:
            y_pred1.append(1)
        else:
            y_pred1.append(0)
    predList.append(y_pred1)
    
#    filename2= "./models/model_lstm_multiStack.hdf5"
#    loaded_model_LSTM = load_model(filename2)
#    y_pred=loaded_model_LSTM.predict(X_Features)
#    y_pred1=[]
#    for x in y_pred:
#        if x>=0.5:
#            y_pred1.append(1)
#        else:
#            y_pred1.append(0)
#    predList.append(y_pred1)
    
    
    predList=pd.DataFrame(predList)
    aggValue=pd.DataFrame(predList).sum()/len(predList)
    
    final_pred=[]
    for x in aggValue:
        if x>=0.5:
            final_pred.append(1)
        else:
            final_pred.append(0)
    
    final_pred=pd.DataFrame(final_pred)
    finalValue=final_pred.sum()/len(final_pred)
    if finalValue[0]>=0.5:
        Onepred='Nepali'
    else:
        Onepred='Non Nepali'
    
    return Onepred


if __name__ == "__main__":
	app.run(debug = False)  