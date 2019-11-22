#importing libraries
import IPython.display as ipd
import os
import pandas as pd
import numpy as np
import librosa
import librosa.display
import glob
from pydub import AudioSegment
import pyaudio
import wave
from xgboost import XGBClassifier
import pickle


# FORMAT = pyaudio.paInt16
# CHANNELS = 2
# RATE = 44100
# CHUNK = 1024
# RECORD_SECONDS = 30
# WAVE_OUTPUT_FILENAME = "file.wav"
 
# audio = pyaudio.PyAudio()
 
# # start Recording
# stream = audio.open(format=FORMAT, channels=CHANNELS,
#                 rate=RATE, input=True,
#                 frames_per_buffer=CHUNK)
# print("recording...")
# frames = []
 
# for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#     data = stream.read(CHUNK)
#     frames.append(data)
# print("finished recording")
 
 
# stop Recording
# stream.stop_stream()
# stream.close()
# audio.terminate()
 
# waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# waveFile.setnchannels(CHANNELS)
# waveFile.setsampwidth(audio.get_sample_size(FORMAT))
# waveFile.setframerate(RATE)
# waveFile.writeframes(b''.join(frames))
# waveFile.close()

#Splitting the file 
newAudio = AudioSegment.from_wav("../static/userRecordingFiles/file.wav")
n=round(len(newAudio)/10000)

for i in range(n):
    m=i*10000
    splitAudio=newAudio[m:m+10000]
    path11='../static/wavSplittedFiles/file' + str(i) +'.wav'
    splitAudio.export(path11, format="wav")
    
#Loading all files and extracting the features
path = '../static/WavSplittedFiles/' 
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
        print("Error encountered while parsing file: ", file)
        
    feature=mfccs
    X_Features.append(feature)

#Updating X for model input
X_Features=pd.DataFrame(X_Features)
X_Features.columns=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
       '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22',
       '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34',
       '35', '36', '37', '38', '39']

filename2= "../models/model_XGB_MixData.sav"
loaded_model_XGB=pickle.load(open(filename2,'rb'))

y_pred=loaded_model_XGB.predict(X_Features)
print(y_pred)