import pyaudio as pa
# Checks to see how many audio input devices are being recognized by PyAudio
p = pa.PyAudio()
for i in range(p.get_device_count()):
	print(p.get_device_info_by_index(i))
