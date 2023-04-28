import numpy as np
import pyaudio as pa
import struct
import matplotlib.pyplot as plt
import socket
import time

p = pa.PyAudio()

CHUNK = 1024
FORMAT = pa.paInt16
CHANNELS = 1
RATE = 48000

#for i in range(p.get_device_count()):
#    print(p.get_device_info_by_index(i))

#def callback1(in_data, frame_count, time_info, flag):
#   input_wave1 = np.fromstring(in_data, 'float32')
#   return (input_wave1, pa.paContinue)

#def callback2(in_data, frame_count, time_info, flag):
#   input_wave2 = np.fromstring(in_data, 'float32')
#   return (input_wave2, pa.paContinue)

stream = p.open(
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
    #stream_callback = callback2
)

fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title("Sound intensity1 Recorded from Robot 1")
ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylabel("Magnitude (dB)")
x_fft = np.linspace(0, RATE, CHUNK)
line_fft1, = ax1.semilogx(x_fft, np.random.rand(CHUNK), 'b')
ax1.set_xlim(20, RATE/2)
ax1.set_ylim(-90, 5)

ax2.set_title("Sound intensity1 Recorded from Robot 2")
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Magnitude (dB)")
x_fft = np.linspace(0, RATE, CHUNK)
line_fft2, = ax2.semilogx(x_fft, np.random.rand(CHUNK), 'b')
ax2.set_xlim(20, RATE/2)
ax2.set_ylim(-90, 5)

fig.show()

# Home
#localIP = "192.168.1.249"
#localPort = 3333
# School
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

mic1_buffer = []
mic2_buffer = []

mic1_start_of_beep = -1.0
mic2_start_of_beep = -1.0

mic1_end_of_beep = -1.0
mic2_end_of_beep = -1.0

mic1_start_index = -2
mic2_start_index = -2

mic1_end_index = -2
mic2_end_index = -2

index = 0
final_time_delay = 0.0
dB_sound_threshold = -45

# Listen for incoming datagrams
print('hi')
while True:
    print('hi2')
    while (mic1_start_index < 0 or mic2_start_index < 0 
           or time.time() - mic1_start_of_beep < 2 or time.time() - mic2_start_of_beep < 2):
        
        print(f"{mic1_start_index} & {mic2_start_index}")
        print(f"{mic1_end_index} & {mic2_end_index}")

        data1 = stream.read(CHUNK)
        dataInt = struct.unpack(str(CHUNK) + 'h', data1)
        intensity1 = np.abs(np.fft.fft(dataInt))*2/(11000*CHUNK)
        intensity1[0:20] = 0.0001
        intensity1[24:] = 0.0001
        # line_fft1.set_ydata(20*np.log10(intensity1))

        data2 = stream2.read(CHUNK)
        dataInt2 = struct.unpack(str(CHUNK) + 'h', data2)
        intensity2 = np.abs(np.fft.fft(dataInt2))*2/(11000*CHUNK)
        intensity2[0:20] = 0.0001
        intensity2[24:] = 0.0001
        # line_fft2.set_ydata(20*np.log10(intensity2))

        mic1_buffer.append(dataInt)
        mic2_buffer.append(dataInt2)

        # fig.canvas.draw()
        # fig.canvas.flush_events()

        # Sound Intensity 1 & 2 from 937.5 Hz to 1078.125 Hz
        sum1 = (intensity1[20] + intensity1[21] + intensity1[22] + intensity1[23]) / 4
        dB_sum1 = 20*np.log10(sum1)

        sum2 = (intensity2[20] + intensity2[21] + intensity2[22] + intensity2[23]) / 4
        dB_sum2 = 20*np.log10(sum2)

        if (mic1_start_of_beep < 0.0 and dB_sum1 >= dB_sound_threshold):
            mic1_start_of_beep = time.time()
            mic1_start_index = index
        #elif (mic1_end_of_beep < 0.0 and dB_sum1 < dB_sound_threshold and mic1_start_of_beep > 0.0):
        #    mic1_end_of_beep = time.time()
        #    mic1_end_index = index

        if (mic2_start_of_beep < 0.0 and dB_sum2 >= dB_sound_threshold):
            mic2_start_of_beep = time.time()
            mic2_start_index = index
        #elif (mic2_end_of_beep < 0.0 and dB_sum2 < dB_sound_threshold and mic2_start_of_beep > 0.0):
        #    mic2_end_of_beep = time.time()
        #    mic2_end_index = index

        index += 1

    print(f"The correlation code is executing\n")

    # CHECK THIS
    T = 2
    dt = 1/44100
    N_before = int(0.5 / dt)
    N_after = int(1.5 / dt)

    print(f"Mic 1 start index is {mic1_start_index} and mic 2 start index is {mic2_start_index}")
    print(f"Mic 1 end index is {mic1_end_index} and mic 2 end index is {mic2_end_index}")

    mic1_start_index = (mic1_start_index * len(dataInt))
    mic2_start_index = (mic2_start_index * len(dataInt))

    mic1_buffer = np.concatenate(mic1_buffer)
    mic2_buffer = np.concatenate(mic2_buffer)

    print(mic1_buffer.shape)

    signal1 = mic1_buffer[mic1_start_index - N_before: mic2_start_index + N_after]
    signal2 = mic2_buffer[mic2_start_index - N_before: mic2_start_index + N_after]

    plt.figure()
    plt.plot(signal1)
    plt.plot(signal2)
    plt.show()

    #mic1_buffer.pop(0)
    #mic1_buffer.append(sum1)
    #mic2_buffer.pop(0)
    #mic2_buffer.append(sum2)

    x1 = np.array(signal1)
    x2 = np.array(signal2)

    x1 = x1 / np.linalg.norm(x1) # normalize the signals
    x2 = x2 / np.linalg.norm(x2)

    print(f"The x1 array is {x1}")
    print('\n')
    print(f"The x2 array is {x2}")

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
    f = 0.5
    max_indices_back = -int(((1 / f) / 2) / dt) + center_index
    max_indices_forward = int(((1 / f) / 2) / dt) + center_index
    i_max_C_normalized = np.argmax(C_x1x2_normalized_per_shift[max_indices_back:max_indices_forward + 1]) + max_indices_back
    print('indices shifted', i_max_C_normalized - center_index)
    t_shift_hat_normalized = t_shift_C[i_max_C_normalized]

    #error_normalized = t_shift_hat_normalized - t_shift_gt
    #print('Estimated time shift with per shift normalization')
    #print('gt time shift {:0.3f} est time shift {:0.3f} error {:0.4f} s {} samples'
    #        .format(t_shift_gt, t_shift_hat_normalized, error_normalized, int(np.round(error_normalized/dt))))

    final_time_delay = t_shift_hat_normalized + abs(mic1_start_of_beep - mic2_start_of_beep)

    # Creating Packet to Send to Mouse
    #bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    #message = bytesAddressPair[0]
    #address = bytesAddressPair[1]
    #clientMsg = "Message from Client: {}".format(message.decode())
    #clientIP  = "Client IP Address: {}".format(address)
    #print(clientMsg)
    #print(clientIP)

    #offset_pack = struct.pack("ff", float(dB_sum1), final_time_delay)
    #UDPServerSocket.sendto(offset_pack, address)


    print(f"Mic 1 beep start is {mic1_start_of_beep} and mic 2 beep start is {mic2_start_of_beep}")
    print(f"Mic 1 beep start - mic 2 beep start is {mic1_start_of_beep - mic2_start_of_beep}")
    print(f"The final time delay is {final_time_delay} and t_shift_hat_normalized is {t_shift_hat_normalized}\n")
        
    mic1_buffer.clear()
    mic2_buffer.clear()

    mic1_start_of_beep = -1.0
    mic2_start_of_beep = -1.0

    mic1_end_of_beep = -1.0
    mic2_end_of_beep = -1.0

    mic1_start_index = -2
    mic2_start_index = -2

    mic1_end_index = -2
    mic2_end_index = -2

    index = 0

    break