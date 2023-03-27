import numpy as np
import pyaudio as pa 
import struct
import matplotlib.pyplot as plt

import socket
import time

CHUNK = 1024
FORMAT = pa.paInt16
CHANNELS = 1
RATE = 48000

p = pa.PyAudio()

stream = p.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

fig, ax = plt.subplots()
ax.title.set_text("Sound Intensity Recorded from Robot 1")
x_fft = np.linspace(0, RATE, CHUNK)
line_fft, = ax.semilogx(x_fft, np.random.rand(CHUNK), 'b')
ax.set_xlim(20,RATE/2)
ax.set_ylim(0,1)
fig.show()

localIP = "192.168.2.102"
localPort = 3333
bufferSize = 1024

# Create a packet to send to the mouse
my_str = '0' 
msgFromServer = my_str.split(' ')
list_int = [int(x) for x in msgFromServer]

my_str2 = '1' 
msgFromServer2 = my_str2.split(' ')
list_int2 = [int(x) for x in msgFromServer2]

val = struct.pack("b"*len(list_int),*list_int)
val2 = struct.pack("b"*len(list_int2),*list_int2)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and ready to send a packet")

# Listen for incoming datagrams
while True:

    data = stream.read(CHUNK)
    dataInt = struct.unpack(str(CHUNK) + 'h', data)
    line_fft.set_ydata(np.abs(np.fft.fft(dataInt))*2/(11000*CHUNK))
    fig.canvas.draw()
    fig.canvas.flush_events()

    max_sound_intensity = max(np.abs(np.fft.fft(dataInt))*2/(11000*CHUNK))
    print(f"Max sound intensity is {max_sound_intensity}")

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    clientMsg = "Message from Client:{}".format(message)
    clientIP  = "Client IP Address:{}".format(address)
    
    print(clientMsg)
    print(clientIP)

    #Creating Packet to Send to Mouse
    offset_pack = struct.pack("f", max_sound_intensity)
    UDPServerSocket.sendto(offset_pack, address)