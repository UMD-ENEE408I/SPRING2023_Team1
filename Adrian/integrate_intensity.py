import numpy as np
import pyaudio as pa
import struct
import matplotlib.pyplot as plt
import socket
import time
from scipy import signal

# Start of PyAudio code which will record sound from two microphones
p = pa.PyAudio()

# Defines microphone parameters such as chunk size, frequency rate of mic, and data format 
CHUNK = 1024
FORMAT = pa.paInt16
CHANNELS = 1
RATE = 44100

# Checks to see how many audio input devices are being recognized by PyAudio
#for i in range(p.get_device_count()):
#    print(p.get_device_info_by_index(i))

# Starts two audio streams "stream1" and "stream2" corresponding to the two microphones
# and sets the different parameters previously declared
stream1 = p.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    output = True,
    frames_per_buffer = CHUNK,
    input_device_index = 1,
)

stream2 = p.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    output = True,
    frames_per_buffer = CHUNK,
    input_device_index = 2,
)

# Creates a matplotlib figure which will display the decibel rating of the two
# sound intensities and their respective frequencies
fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title("Sound Intensity Recorded from Robot 1")
ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylabel("Magnitude (dB)")
x_fft = np.linspace(0, RATE, CHUNK)
line_fft1, = ax1.semilogx(x_fft, np.random.rand(CHUNK), 'b')
ax1.set_xlim(20, RATE/2)
ax1.set_ylim(-90, 5)

ax2.set_title("Sound Intensity Recorded from Robot 2")
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Magnitude (dB)")
x_fft = np.linspace(0, RATE, CHUNK)
line_fft2, = ax2.semilogx(x_fft, np.random.rand(CHUNK), 'b')
ax2.set_xlim(20, RATE/2)
ax2.set_ylim(-90, 5)

#fig.show()

# START OF NETWORK CODE
# 
# The following code involves the networking aspect which communicates with the robot
# by creating packets to send to the robot

# Home network settings
# localIP = "192.168.1.249"
# localPort = 3333
# bufferSize = 1024

# School network settings
localIP = "192.168.2.102"
localPort = 3333
bufferSize = 1024

"""# Create a packet to send to the mouse
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
print("UDP server up and ready to send a packet")"""

# END OF NETWORK CODE

# START OF TIME DELAY CALCULATION
#
# The following code calculates the time delay between two different microphones

mic1_buffer = []
mic2_buffer = []

mic1_start_of_beep = -1.0
mic2_start_of_beep = -1.0

mic1_start_index = -2
mic2_start_index = -2

mic_proximity = 0

index = 0
final_time_delay = 0.0
dB_sound_threshold = -45

# Start of main loop
while True:

    # Start of second loop
    #
    # This while loop will only run if any of the following four conditions are true:
    # 1. Mic 1's start beep index has not been set
    # 2. Mic 2's start beep index has not been set
    # 3. Less than two seconds have passed since (current time) - (time at which mic 1's beep was recorded)
    # 4. Less than two seconds have passed since (current time) - (time at which mic 2's beep was recorded)
    while (mic1_start_index < 0 or mic2_start_index < 0 
           or time.time() - mic1_start_of_beep < 2 or time.time() - mic2_start_of_beep < 2):
        
        print(f"{mic1_start_index} & {mic2_start_index}")
        
        # The variables data1 and data2 receive the bytes which contain actual sound data
        # from the two microphones
        # 
        # This is then unpacked into dataInt1 and dataInt2
        # 
        # Intensity is then calculated by taking the fft of this sound data
        # 
        # Intensities not between 937.5 Hz to 1078.125 Hz are set to 0
        data1 = stream1.read(CHUNK)
        dataInt1 = struct.unpack(str(CHUNK) + 'h', data1)
        intensity1 = np.abs(np.fft.fft(dataInt1))*2/(11000*CHUNK)
        intensity1[0:20] = 0.0001
        intensity1[24:] = 0.0001
        # line_fft1.set_ydata(20*np.log10(intensity1))

        data2 = stream2.read(CHUNK)
        dataInt2 = struct.unpack(str(CHUNK) + 'h', data2)
        intensity2 = np.abs(np.fft.fft(dataInt2))*2/(11000*CHUNK)
        intensity2[0:20] = 0.0001
        intensity2[24:] = 0.0001
        # line_fft2.set_ydata(20*np.log10(intensity2))

        # Arrays which contain the unpacked sound data from the microphones
        mic1_buffer.append(dataInt1)
        mic2_buffer.append(dataInt2)

        # fig.canvas.draw()
        # fig.canvas.flush_events()

        # Average sound intensities 1 & 2 from 937.5 Hz to 1078.125 Hz
        sum1 = (intensity1[20] + intensity1[21] + intensity1[22] + intensity1[23]) / 4
        dB_sum1 = 20*np.log10(sum1)

        sum2 = (intensity2[20] + intensity2[21] + intensity2[22] + intensity2[23]) / 4
        dB_sum2 = 20*np.log10(sum2)

        # Records the start of the beep for both mic 1 and mic 2
        # In addition, it stores the index of the buffer arrays at which this occured
        if (mic1_start_of_beep < 0.0 and dB_sum1 >= dB_sound_threshold):
            mic1_start_of_beep = time.time()
            mic1_start_index = index

        if (mic2_start_of_beep < 0.0 and dB_sum2 >= dB_sound_threshold):
            mic2_start_of_beep = time.time()
            mic2_start_index = index
        index += 1 # This index is used to calculate at what index do the microphones record the start of the beep

    time_delay = mic1_start_of_beep - mic2_start_of_beep

    if (time_delay > 0):
        mic_proximity = 2 # Mic 2 is closer
    elif (time_delay < 0):
        mic_proximity = 1 # Mic 1 is closer
    elif (time_delay == 0):
        mic_proximity = 3 # Mic 1 and mic 2 are equidistant
    print(f"Final time delay is {final_time_delay} and difference is {mic1_start_of_beep - mic2_start_of_beep}")

    # END OF CORRELATION CODE

    # START OF NETWORK CODE
    # 
    # Creating Packet to Send to Mouse
    # bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    # message = bytesAddressPair[0]
    # address = bytesAddressPair[1]
    # clientMsg = "Message from Client: {}".format(message.decode())
    # clientIP  = "Client IP Address: {}".format(address)
    # print(clientMsg)
    # print(clientIP)
    # offset_pack = struct.pack("ff", float(dB_sum1), final_time_delay)
    # UDPServerSocket.sendto(offset_pack, address)
    #
    # END OF NETWORK CODE

    # Print statements which test functionality
    # print(f"Mic 1 beep start is {mic1_start_of_beep} and mic 2 beep start is {mic2_start_of_beep}")
    # print(f"Mic 1 beep start - mic 2 beep start is {mic1_start_of_beep - mic2_start_of_beep}")
    # print(f"The final time delay is {final_time_delay} and t_shift_hat_normalized is {t_shift_hat_normalized}\n")
    
    # The following code only executes after the final time delay is calculated
    # After this occurs everything is reset so the 2nd while loop (which populates the buffer arrays)
    # can start fresh to calculate a new final time delay
    mic1_buffer.clear()
    mic2_buffer.clear()

    mic1_start_of_beep = -1.0
    mic2_start_of_beep = -1.0

    mic1_start_index = -2
    mic2_start_index = -2

    mic_proximity = 0

    index = 0

    break # Ends the script, but is only in place to test functionality