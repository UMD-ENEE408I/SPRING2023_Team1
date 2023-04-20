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
ax.set_title("Sound Intensity Recorded from Robot 1")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Magnitude (dB)")
x_fft = np.linspace(0, RATE, CHUNK)
line_fft, = ax.semilogx(x_fft, np.random.rand(CHUNK), 'b')
ax.set_xlim(20, RATE/2)
ax.set_ylim(-90, 5)
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

t_py = []
x2_py = []
python_max = 0.0

# Listen for incoming datagrams
while True:

    data = stream.read(CHUNK)
    dataInt = struct.unpack(str(CHUNK) + 'h', data)
    intensity = np.abs(np.fft.fft(dataInt))*2/(11000*CHUNK)
    intensity[0:20] = 0.0001
    intensity[24:] = 0.0001
    line_fft.set_ydata(20*np.log10(intensity))
    fig.canvas.draw()
    fig.canvas.flush_events()

    # Sound Intensity from 937.5 Hz to 1078.125 Hz
    sum = (intensity[20] + intensity[21] + intensity[22] + intensity[23]) / 4
    dB_sum = 20*np.log10(sum)
    if (dB_sum >= -45):
        print(f"Sound intensity (dB) between 937.5 Hz and 1078.125 Hz is {dB_sum}")

    # Creating Packet to Send to Mouse

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    clientMsg = "Message from Client: {}".format(message.decode())
    clientIP  = "Client IP Address: {}".format(address)
    
    print(clientMsg)
    print(clientIP)

    #####
    if (len(t_py) < 50) and (len(x2_py) < 50):
        t_py.append(float(message.decode()))
        x2_py.append(dB_sum)
        print(f"Length of t_py is {len(t_py)} and length of x2_py is {x2_py}\n")

    if ((len(t_py) == 50) and (len(x2_py) == 50)):

        print(f"The correlation code is executing and the type of t is {type(t_py[1])}\n")

        t_py.pop(0)
        t_py.append(float(message.decode()))
        x2_py.pop(0)
        x2_py.append(dB_sum)

        # Make some sinusoids to find the timeshift between
        dt = 0.001
        T = 2.0
        f = 1

        t = np.array(t_py)
        x2 = np.array(x2_py)

        #t = message.decode()
        x1 = np.cos(f*2*np.pi*t) # General sinusoid chosen
        x1 = x1 / np.linalg.norm(x1) # normalize the signals

        #x2 = dB_sum # Actual sound intensity from microphone
        x2 = x2 / np.linalg.norm(x2)

        # Calculate the correlation and the corresponding timeshift corresponding to each index
        C_x1x2 = np.correlate(x1, x2, mode='full')
        t_shift_C = np.arange(-T+dt, T, dt)

        # Attempt to estimate the time shift using the correlation directly
        # without normalizing by how much x1 and x2 overlapped when calculating
        # each element of the correlation
        i_max_C = np.argmax(C_x1x2)
        t_shift_hat = t_shift_C[i_max_C]

        # Without the per sample normalization there will be an error of
        # several samples in the estimated timeshift.
        # This is because the maximum of the correlation only corresponds
        # to the maximum match if the signals correlated have equal magnitude
        # at each shift
        #error = t_shift_hat - t_shift_gt
        #print('Estimated time shift without per shift normalization')
        #print('gt time shift {:0.3f} est time shift {:0.3f} error {:0.4f} s {} samples'
        #    .format(t_shift_gt, t_shift_hat, error, int(np.round(error/dt))))

        # Calculate the magnitude of the portion of x1 that overlapped with x2
        # and vice versa for each sample in C_x1x2
        C_normalization_x1 = np.zeros(C_x1x2.shape[0])
        C_normalization_x2 = np.zeros(C_x1x2.shape[0])

        center_index = int((C_x1x2.shape[0] + 1) / 2) - 1 # Index corresponding to zero shift
        low_shift_index  = -int((C_x1x2.shape[0] + 1) / 2) + 1
        high_shift_index =  int((C_x1x2.shape[0] + 1) / 2) - 1
        for i in range(low_shift_index, high_shift_index + 1):
            low_norm_index  = max(0, i)
            high_norm_index = min(x1.shape[0], i + x1.shape[0])
            C_normalization_x1[i+center_index] = np.linalg.norm(x1[low_norm_index:high_norm_index])

            low_norm_index  = max(0, -i)
            high_norm_index = min(x2.shape[0], -i + x2.shape[0])
            C_normalization_x2[i+center_index] = np.linalg.norm(x2[low_norm_index:high_norm_index])

        # Normalize the calculated correlation per shift
        C_x1x2_normalized_per_shift = C_x1x2 / (C_normalization_x1 * C_normalization_x2)

        # Search for the maximum at most a half period back and forward due to periodicity of the input signal
        # and the fact that per shift normalization causes peaks a full period to have approximately equal magnitude
        # to the closest peak in the normalized correlation
        max_indices_back = -int(((1 / f) / 2) / dt) + center_index
        max_indices_forward = int(((1 / f) / 2) / dt) + center_index
        i_max_C_normalized = np.argmax(C_x1x2_normalized_per_shift[max_indices_back:max_indices_forward + 1]) + max_indices_back
        t_shift_hat_normalized = t_shift_C[i_max_C_normalized]

        #error_normalized = t_shift_hat_normalized - t_shift_gt
        #print('Estimated time shift with per shift normalization')
        #print('gt time shift {:0.3f} est time shift {:0.3f} error {:0.4f} s {} samples'
        #        .format(t_shift_gt, t_shift_hat_normalized, error_normalized, int(np.round(error_normalized/dt))))

        python_max = t_shift_hat_normalized
        #####

    offset_pack = struct.pack("ff", float(dB_sum), python_max)
    UDPServerSocket.sendto(offset_pack, address)

    print(f"The dB_sum is {dB_sum} and python_max is {python_max}\n")