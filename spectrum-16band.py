#System-Import
import sys
import numpy as np #fuer fft-analyse
from struct import unpack #zum interpretieren der daten
import time
import argparse
import random
import math
import pyaudio #fuer audiointerfacing
from neopixel import *

#Haupt-Matrix anlegen, in der der displayinhalt aufgebaut wird
#2 dimensionen für die pixel, 3. dimension für die farbe
c, w, h = 3, 8, 16;
Matrix = [[[0 for x in range(w)] for x in range(w)] for y in range(h)] 

# LED strip config
LED_COUNT      = 128      
LED_PIN        = 18      #hier wird IO-Pin 18 definiert
LED_FREQ_HZ    = 800000  
LED_DMA        = 10      
LED_BRIGHTNESS = 50      
LED_INVERT     = False   
LED_CHANNEL    = 0       

#Definitionen
no_channels = 1
sample_rate = 44100
device = 2
chunk = 2822  #vielfaches von 8! 3072
movement=0

#Listen generieren
switched = [0,2,4,6,8,10,12,14] # umgedrehte reihen, da die pixelmatrix schlangenlinienfoermig ist
spectralvalues = [1,2,3,4,5,6,7,8,7,6,5,4,3,2,1,0]
matrix = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
power = []
weighting = [3,3,4,4,6,8,8,12,16,16,35,35,64,64,64,64]  #weighting der spektralbaender


#ZITAT: Power Array Index Funktion
def piff(val):
    return int(2*chunk*val/sample_rate)
#ZITAT Ende

#Audio Setup pyaudio mit dem USB Interface
p = pyaudio.PyAudio()
stream = p.open(
    format = pyaudio.paInt16,
    channels = no_channels,
    rate = sample_rate,
    input = True,
    frames_per_buffer = chunk,
    input_device_index = device)

def calculate_levels(data, chunk,sample_rate):
    #ZITAT: Umwandlung des Streams in eine Matrix
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
    #ZITAT Ende
    #einzelne baender berechnen
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
    #Werte auf 0-8 beschraenken und zurueckgeben
    matrix=matrix.clip(0,8)
    return matrix

#MAIN LOOP
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
            
            #Audio-Stream in Chunks kopieren               
            data = stream.read(chunk)
            
            #Matrix-Audiolevel berechnen lassen
            spectralvalues=calculate_levels(data, chunk,sample_rate)
                             
            #Matrix auswerten  
            for x in range (0,16):
                for y in range (0,8):   
			#volle pixel zeigen den wert             
                    if (spectralvalues[x]-y)>1:
                        Matrix[x][y][2] = 255
                        Matrix[x][y][1] = int(y*255/7)
                        #Matrix[x][y][1] = 0
			#nachkommastelle wird in der helligkeit des obersten pixels dargestellt
                    elif (spectralvalues[x]-y)<1 and (spectralvalues[x]-y)>0:
                        Matrix[x][y][2] = int((spectralvalues[x]-y)*255)
                        Matrix[x][y][1] = int((spectralvalues[x]-y)*255)
                    else:
                        Matrix[x][y][0] = 0
                        Matrix[x][y][1] = 0
                        Matrix[x][y][2] = 0
                   
                                                
            #matrix auf den strip uebertragen  
            for x in range (0,16):
                for y in range (0,8):
			#leds sind in schlangenlinien, daher jede zweite reihe invers
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

