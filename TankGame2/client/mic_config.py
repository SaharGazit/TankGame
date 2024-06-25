import pyaudio

def select_microphone(index):
    # Get the device info
    device_info = p.get_device_info_by_index(index)
    # Check if this device is a microphone (an input device)
    if device_info.get('maxInputChannels') > 0:
      print(f"Selected Microphone: {device_info.get('name')}")
    else:
      print(f"No microphone at index {index}")


# Select a microphone with a specific index

# Create an instance of PyAudio
p = pyaudio.PyAudio()

# Get the number of audio I/O devices
devices = p.get_device_count()

# Iterate through all devices
for i in range(devices):
   # Get the device info
   device_info = p.get_device_info_by_index(i)
   # Check if this device is a microphone (an input device)
   if device_info.get('maxInputChannels') > 0:
      print(f"Microphone: {device_info.get('name')} , Device Index: {device_info.get('index')}")

print("enter mic index: ", end = "")
input_index = int(input())
select_microphone(input_index)
print("enter speaker index: ", end = "")
output_index = int(input())
select_microphone(output_index)

sound  = True
CHUNK = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "output.wav"

stream_input = p.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=RATE,
                      input=True, # for mic
                      output=True,
                      input_device_index = input_index,
                      frames_per_buffer=CHUNK)
print("* recording")
print("* done recording")
#stream_input.stop_stream()
#stream_input.close()
stream_output = p.open( format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True, # for speaker
                        input_device_index = output_index,
                        frames_per_buffer=CHUNK)
frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream_input.read(CHUNK)
    frames.append(data)
    stream_input.write(data)


#for f in frames:
#    stream_input.write(f) #digital to analog

p.terminate()