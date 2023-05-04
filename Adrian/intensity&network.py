def correlation_algo(stream1, stream2):

    mic1_buffer = []
    mic2_buffer = []

    mic1_start_of_beep = -1.0
    mic2_start_of_beep = -1.0

    mic1_start_index = -2
    mic2_start_index = -2

    index = 0
    final_time_delay = 0.0
    dB_sound_threshold = -45

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

    # START OF CORRELATION CODE
    print(f"The correlation code is executing\n")

    T = 2
    dt = 1/44100
    N_before = int(0.5 / dt)
    N_after = int(1.5 / dt)

    print(f"Mic 1 start index is {mic1_start_index} and mic 2 start index is {mic2_start_index}")
 
    mic1_start_index = (mic1_start_index * len(dataInt1))
    mic2_start_index = (mic2_start_index * len(dataInt1))

    np_mic1_buffer = np.concatenate(mic1_buffer)
    np_mic2_buffer = np.concatenate(mic2_buffer)

    print(np_mic1_buffer.shape)

    signal1 = np_mic1_buffer[mic1_start_index - N_before: mic1_start_index + N_after]
    signal2 = np_mic2_buffer[mic2_start_index - N_before: mic2_start_index + N_after]

    # Test plots to ensure functionality
    # plt.figure()
    # plt.plot(signal1)
    # plt.plot(signal2)
    # plt.show()

    x1 = np.array(signal1)
    x2 = np.array(signal2)

    x1 = x1 / np.linalg.norm(x1) # normalize the signals
    x2 = x2 / np.linalg.norm(x2)

    print(f"The x1 array is {x1.shape}") # These are test print statements to confirm functionality
    print(f"The x2 array is {x2.shape}")

    # Calculate the correlation and the corresponding timeshift corresponding to each index
    C_x1x2 = signal.correlate(x1, x2, mode='full')
    print(C_x1x2)
    t_shift_C = np.arange(-T+dt, T, dt)
    print(t_shift_C)

    # Attempt to estimate the time shift using the correlation directly
    # without normalizing by how much x1 and x2 overlapped when calculating
    # each element of the correlation
    i_max_C = np.argmax(C_x1x2)
    print(i_max_C)
    t_shift_hat = t_shift_C[i_max_C]
    print(t_shift_hat)

    # Calculate the magnitude of the portion of x1 that overlapped with x2
    # and vice versa for each sample in C_x1x2
    C_normalization_x1 = np.zeros(C_x1x2.shape[0])
    C_normalization_x2 = np.zeros(C_x1x2.shape[0])
    print(C_normalization_x1)

    center_index = int((C_x1x2.shape[0] + 1) / 2) - 1 # Index corresponding to zero shift

    print('norming')
    x1_ones = np.ones((x1.shape[0],))
    x1_square = np.square(x1)
    x1_sum_square = signal.correlate(x1_square, x1_ones, 'full')
    C_normalization_x1 = np.sqrt(x1_sum_square)

    x2_ones = np.ones((x2.shape[0],))
    x2_square = np.square(x2)
    x2_sum_square = signal.correlate(x2_square, x2_ones, 'full')
    C_normalization_x2 = np.flip(np.sqrt(x2_sum_square))
    print('normed')

    print(f"Check {C_normalization_x2}")

    # Normalize the calculated correlation per shift
    C_x1x2_normalized_per_shift = C_x1x2 / (C_normalization_x1 * C_normalization_x2)

    # Search for the maximum at most a half period back and forward due to periodicity of the input signal
    # and the fact that per shift normalization causes peaks a full period to have approximately equal magnitude
    # to the closest peak in the normalized correlation
    f = 0.5
    max_indices_back = -int(((1 / f) / 2) / dt) + center_index
    max_indices_forward = int(((1 / f) / 2) / dt) + center_index
    i_max_C_normalized = np.argmax(C_x1x2_normalized_per_shift[max_indices_back:max_indices_forward + 1]) + max_indices_back
    # print('indices shifted', i_max_C_normalized - center_index)
    t_shift_hat_normalized = t_shift_C[i_max_C_normalized]

    final_time_delay = t_shift_hat_normalized

    # END OF CORRELATION CODE

    # Print statements which test functionality
    print(f"Mic 1 beep start is {mic1_start_of_beep} and mic 2 beep start is {mic2_start_of_beep}")
    print(f"Mic 1 beep start - mic 2 beep start is {mic1_start_of_beep - mic2_start_of_beep}")
    print(f"The final time delay is {final_time_delay} and t_shift_hat_normalized is {t_shift_hat_normalized}\n")
    
    # The following code only executes after the final time delay is calculated
    # After this occurs everything is reset so the 2nd while loop (which populates the buffer arrays)
    # can start fresh to calculate a new final time delay
    mic1_buffer.clear()
    mic2_buffer.clear()

    mic1_start_of_beep = -1.0
    mic2_start_of_beep = -1.0

    mic1_start_index = -2
    mic2_start_index = -2

    index = 0

    return final_time_delay

import numpy as np
import pyaudio as pa
import struct
import matplotlib.pyplot as plt
import time
from scipy import signal
from scipy import linalg

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
# fig.show()

# START OF TIME DELAY CALCULATION
#
# The following code calculates the time delay offset between two different microphones
# The loop runs 10 times to calculate the average time delay "error"
count = 0
time_delay_list = []
while (count < 10):
    time_delay_list.append(correlation_algo(stream1, stream2))
    count += 1

avg_time_offset = sum(time_delay_list)/len(time_delay_list)

# The following code calculates the real time delay between two different microphones
# The time delay offset is subtracted from the final time delay to calculate which mic
# is closer to the sound source
while True:

    final_time_delay = correlation_algo(stream1, stream2)
    final_time_delay = final_time_delay - avg_time_offset