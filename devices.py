#System-Import
import sys
import pyaudio #für audio device
import numpy as np #für fft
from struct import unpack #zum interpretieren der daten

#Definitionen
no_channels = 1
sample_rate = 44100
device = 2
chunk = 3072

spectrum = [1,1,1,3,3,3,2,2]
matrix = [0,0,0,0,0,0,0,0]
power = []
weighting = [2,8,8,16,16,32,32,64]


#Audio Setup pyaudio
p = pyaudio.PyAudio()
stream = p.open(
    format = pyaudio.paInt16,
    channels = no_channels,
    rate = sample_rate,
    input = True,
    frames_per_buffer = chunk,
    input_device_index = device)


#Device-Uebersicht generieren
def list_devices():
    print('Available Audio devices:')
    audio = pyaudio.PyAudio()
    devicecount = audio.get_device_count()
    i = 0
    while i < devicecount:
        dev = audio.get_device_info_by_index(i)
        print(str(i)+'. '+dev['name'])
        print(' Inputs: '+ str(dev['maxInputChannels'])+ ' Outputs: '+ str(dev['maxOutputChannels']))
        i += 1

list_devices()

#Power Array Index
def piff(val):
    return int(2*chunk*val/sample_rate)

def calculate_levels(data, chunk,sample_rate):
    global matrix
    data = unpack("%dh"%(len(data)/2),data)
    data = np.array(data, dtype='h')
    fourier=np.fft.rfft(data)
    fourier=np.delete(fourier,len(fourier)-1)
    power = np.abs(fourier)
    matrix[0]= int(np.mean(power[piff(0) :piff(156):1]))
    matrix[1]= int(np.mean(power[piff(156) :piff(313):1]))
    matrix[2]= int(np.mean(power[piff(313) :piff(625):1]))
    matrix[3]= int(np.mean(power[piff(625) :piff(1250):1]))
    matrix[4]= int(np.mean(power[piff(1250) :piff(2500):1]))
    matrix[5]= int(np.mean(power[piff(2500) :piff(5000):1]))
    matrix[6]= int(np.mean(power[piff(5000) :piff(10000):1]))
    matrix[7]= int(np.mean(power[piff(10000):piff(20000):1]))
    matrix=np.divide(np.multiply(matrix,weighting),1000000)
    matrix=matrix.clip(0,8)
    return matrix

#Einmalig Daten ausgeben
data = stream.read(chunk) #Audio-Stream in CHunks kopieren
matrix=calculate_levels(data, chunk,sample_rate)
print(str(data))
print(str(matrix))

#Main Loop
while 1:
    try:


    except KeyboardInterrupt:
        print("Ctrl-C Terminating...")
        stream.stop_stream()
        stream.close()
        p.terminate()
        sys.exit(1)
        
        
                    #werte generieren
            #for x in range (0,16):
            #    spectralvalues[x] =  abs(5*math.sin((math.pi/6)*x+movement)+5)
               
