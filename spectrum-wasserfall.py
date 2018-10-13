#System-Import
import sys
import numpy as np #fuer fft
from struct import unpack #zum interpretieren der daten
import time
import argparse
import random
import math
import pyaudio
from neopixel import *

#Haupt-Matrix anlegen
c, w, h = 3, 8, 16;
Matrix = [[[0 for c in range(w)] for x in range(w)] for y in range(h)] 

# LED strip config
LED_COUNT      = 128      
LED_PIN        = 18      #hier 18!
LED_FREQ_HZ    = 800000  
LED_DMA        = 10      
LED_BRIGHTNESS = 100     # 30 ist gudd
LED_INVERT     = False   
LED_CHANNEL    = 0       



#Definitionen
no_channels = 1
sample_rate = 44100
device = 2
chunk = 2822  #vielfaches von 8! 3072
movement=0

#Listen
#switched = [1,3,5,7,9,11,13,15]
switched = [0,2,4,6,8,10,12,14]
spectralvalues = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
spectralvalues2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
spectralvalues3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
spectralvalues4 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
spectralvalues5 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
spectralvalues6 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
spectralvalues7 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
spectralvalues8 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
matrix = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
power = []
weighting = [3,3,4,4,6,8,8,12,16,16,35,35,64,64,64,64]


#Power Array Index
def piff(val):
    return int(2*chunk*val/sample_rate)

#Audio Setup pyaudio
p = pyaudio.PyAudio()
stream = p.open(
    format = pyaudio.paInt16,
    channels = no_channels,
    rate = sample_rate,
    input = True,
    frames_per_buffer = chunk,
    input_device_index = device)

#ZITAT: Umwandlung des Streams in eine Matrix
def calculate_levels(data, chunk,sample_rate):
    global matrix
    #ascii-daten in numpy array stecken
    data = unpack("%dh"%(len(data)/2),data)
    data = np.array(data, dtype='h')
    #FFT anwenden
    fourier=np.fft.rfft(data)
    #Array zuschneiden
    fourier=np.delete(fourier,len(fourier)-1)
    #amplitude pro band berechnen
    power = np.abs(fourier)
    matrix[0]= np.mean(power[piff(0) :piff(17):1])
    matrix[1]= np.mean(power[piff(17) :piff(28):1])
    matrix[2]= np.mean(power[piff(42) :piff(69):1])
    matrix[3]= np.mean(power[piff(69) :piff(110):1])
    matrix[4]= np.mean(power[piff(110) :piff(180):1])
    matrix[5]= np.mean(power[piff(180) :piff(290):1])
    matrix[6]= np.mean(power[piff(290) :piff(480):1])
    matrix[7]= np.mean(power[piff(480):piff(750):1])
    matrix[8]= np.mean(power[piff(750) :piff(1100):1])
    matrix[9]= np.mean(power[piff(1100) :piff(2000):1])
    matrix[10]= np.mean(power[piff(2000) :piff(3300):1])
    matrix[11]= np.mean(power[piff(3300) :piff(5500):1])
    matrix[12]= np.mean(power[piff(5500) :piff(7000):1])
    matrix[13]= np.mean(power[piff(7000) :piff(8000):1])
    matrix[14]= np.mean(power[piff(8000) :piff(10000):1])
    matrix[15]= np.mean(power[piff(10000) :piff(20000):1])
    #aufraeumen
    matrix=np.divide(np.multiply(matrix,weighting),100)
    matrix=np.log10(matrix)
    matrix=matrix-3
    matrix=matrix*3
    #Werte auf 0-8 beschraenken
    matrix=matrix.clip(0,8)
    return matrix

#MAIN
if __name__ == '__main__':
    #Argumente
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='display clear')
    args = parser.parse_args()

    #NeoPixel initialisieren
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print ('Ctrl-C zum beenden')

    #hauptschleife
    try:
        while True:
            
            #Audio-Stream in CHunks kopieren               
            data = stream.read(chunk)
            
            for x in range (0,16):
                spectralvalues8[x] = spectralvalues7[x]
                spectralvalues7[x] = spectralvalues6[x]
                spectralvalues6[x] = spectralvalues5[x]
                spectralvalues5[x] = spectralvalues4[x]
                spectralvalues4[x] = spectralvalues3[x]
                spectralvalues3[x] = spectralvalues2[x]
                spectralvalues2[x] = spectralvalues[x]
            
            #print(str(spectralvalues) + ' -> ' + str(spectralvalues2))
            
            #werte berechnen
            spectralvalues=calculate_levels(data, chunk,sample_rate)
                             
            #matrix auswerten
            noisefloor=3
            for x in range (0,16):
                    Matrix[x][0][2] = int((spectralvalues[x]-noisefloor)/8*255)
                    Matrix[x][0][1] = int((spectralvalues[x]-5)/3*255)
                    Matrix[x][0][0] = int((spectralvalues[x]-7)*255)
                    Matrix[x][1][2] = int((spectralvalues2[x]-noisefloor)/8*255)
                    Matrix[x][1][1] = int((spectralvalues2[x]-5)/3*255)
                    Matrix[x][1][0] = int((spectralvalues2[x]-7)*255)
                    Matrix[x][2][2] = int((spectralvalues3[x]-noisefloor)/8*255)
                    Matrix[x][2][1] = int((spectralvalues3[x]-5)/3*255)
                    Matrix[x][2][0] = int((spectralvalues3[x]-7)*255)
                    Matrix[x][3][2] = int((spectralvalues4[x]-noisefloor)/8*255)
                    Matrix[x][3][1] = int((spectralvalues4[x]-5)/3*255)
                    Matrix[x][3][0] = int((spectralvalues4[x]-7)*255)
                    Matrix[x][4][2] = int((spectralvalues5[x]-noisefloor)/8*255)
                    Matrix[x][4][1] = int((spectralvalues5[x]-5)/3*255)
                    Matrix[x][4][0] = int((spectralvalues5[x]-7)*255)
                    Matrix[x][5][2] = int((spectralvalues6[x]-noisefloor)/8*255)
                    Matrix[x][5][1] = int((spectralvalues6[x]-5)/3*255)
                    Matrix[x][5][0] = int((spectralvalues6[x]-7)*255)
                    Matrix[x][6][2] = int((spectralvalues7[x]-noisefloor)/8*255)
                    Matrix[x][6][1] = int((spectralvalues7[x]-5)/3*255)
                    Matrix[x][6][0] = int((spectralvalues7[x]-7)*255)
                    Matrix[x][7][2] = int((spectralvalues8[x]-noisefloor)/8*255)
                    Matrix[x][7][1] = int((spectralvalues8[x]-5)/3*255)
                    Matrix[x][7][0] = int((spectralvalues8[x]-7)*255)
        
                                                
            #matrix updaten           
            for x in range (0,16):
                for y in range (0,8):
                    if Matrix[x][y][1] < 0:
                            Matrix[x][y][1] = 0
                    if Matrix[x][y][2] < 0:
                            Matrix[x][y][2] = 0
                    if Matrix[x][y][0] < 0:
                            Matrix[x][y][0] = 0
                            
                    if x in switched:
                        p = 8*x + y
                    else:
                        p = 8*x + (7-y)
                    strip.setPixelColorRGB(p,Matrix[x][y][0],Matrix[x][y][1],Matrix[x][y][2])
                    #print('set pixel '+ str(p) + ' to' + ' R: ' +str(Matrix[x][y][0])+ ' G: ' +str(Matrix[x][y][1])+ ' B: ' +str(Matrix[x][y][2]))
                    
            strip.show()
           
    except KeyboardInterrupt:
        if args.clear:
            for x in range (0,16):
                for y in range (0,8):
                    strip.setPixelColorRGB(p,0,0,0)

