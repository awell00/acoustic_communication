import numpy as np
import sounddevice as sd
from scipy.io.wavfile import read, write
from scipy.signal import find_peaks
from scipy.fft import fft
from tqdm import tqdm
import time
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
from scipy import signal
import gradio as gr
import reedsolo
import wavio
from scipy.signal import butter, lfilter

#---------------Parameters---------------#

low_frequency = 18000
high_frequency = 19000 
bit_duration = 0.007
sample_rate = 44100
amplitude_scaling_factor = 10.0

#-----------------Record-----------------#

def record(audio):
    try:
        sr, data = audio
        wavio.write("recorded.wav", data, sr)
        main()
        return f"Audio receive correctly"
    except Exception as e:
        return f"Error: {e}"

#-----------------Filter-----------------#

def butter_bandpass(lowcut, highcut, sr, order=5):
    nyquist = 0.5 * sr
    low = lowcut / nyquist
    high = highcut / nyquist
    coef = butter(order, [low, high], btype='band')
    b = coef[0]
    a = coef[1]
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, sr, order=5):
    b, a = butter_bandpass(lowcut, highcut, sr, order=order)
    y = lfilter(b, a, data)
    return y

def main():
    input_file = 'recorded.wav'
    output_file = 'output_filtered_receiver.wav'
    lowcut = 17500
    highcut = 19500

    sr, data = read(input_file)

    filtered_data = butter_bandpass_filter(data, lowcut, highcut, sr)
    write(output_file, sr, np.int16(filtered_data))
    return "Filtered Audio Generated"

#-----------------Frame-----------------#

def calculate_snr(data, start, end, target_frequency, sample_rate):

    segment = data[start:end]
    spectrum = np.fft.fft(segment)
    frequencies = np.fft.fftfreq(len(spectrum), 1 / sample_rate)
    target_index = np.abs(frequencies - target_frequency).argmin()
    amplitude = np.abs(spectrum[target_index])

    noise_segment = data[100:1000+len(segment)]
    noise_spectrum = np.fft.fft(noise_segment)
    noise_amplitude = np.abs(noise_spectrum[target_index])

    snr = 10 * np.log10(amplitude / noise_amplitude)
    return snr
    
filename = 'output_filtered_receiver.wav'

def frame_analyse(filename):
    sr, y = read(filename)

    first_part_start = 0
    first_part_end = len(y) // 2

    second_part_start = len(y) // 2
    second_part_end = len(y)

    nperseg = 256
    noverlap = 128

    f, t, Sxx = signal.spectrogram(y, sr, nperseg=nperseg, noverlap=noverlap)

    plt.figure()
    plt.pcolormesh(t, f, Sxx, shading="gouraud")
    plt.xlabel("Time [s]")
    plt.ylabel("Frequency [Hz]")
    plt.title("Spectrogram of the signal")
    plt.show()

    f0 = 18000

    f_idx = np.argmin(np.abs(f - f0))

    thresholds_start = calculate_snr(y, first_part_start, first_part_end, low_frequency, sample_rate)
    thresholds_end = calculate_snr(y, second_part_start, second_part_end, high_frequency, sample_rate)

    t_idx_start = np.argmax(Sxx[f_idx] > thresholds_start)

    t_start = t[t_idx_start]

    t_idx_end = t_idx_start
    while t_idx_end < len(t) and np.max(Sxx[f_idx, t_idx_end:]) > thresholds_end:
        t_idx_end += 1

    t_end = t[t_idx_end]

    return t_start, t_end

#-----------------Receiver-----------------#

def dominant_frequency(signal, sample_rate=44100):
    yf = fft(signal)
    xf = np.linspace(0.0, sample_rate / 2.0, len(signal) // 2)
    peaks, _ = find_peaks(np.abs(yf[0:len(signal) // 2]))
    return xf[peaks[np.argmax(np.abs(yf[0:len(signal) // 2][peaks]))]]

def binary_to_text(binary):
    try:
      return ''.join(chr(int(binary[i:i + 8], 2)) for i in range(0, len(binary), 8))
    except Exception as e:
      return f"Except: {e}"

def decode_rs(binary_string, ecc_bytes):
    byte_data = bytearray(int(binary_string[i:i+8], 2) for i in range(0, len(binary_string), 8))
    rs = reedsolo.RSCodec(ecc_bytes)
    corrected_data_tuple = rs.decode(byte_data)
    corrected_data = corrected_data_tuple[0]

    corrected_data = corrected_data.rstrip(b'\x00')

    corrected_binary_string = ''.join(format(byte, '08b') for byte in corrected_data)

    return corrected_binary_string

def manchester_decoding(binary_string):
    decoded_string = ''
    for i in tqdm(range(0, len(binary_string), 2), desc="Decoding"):
        if i + 1 < len(binary_string):
            if binary_string[i] == '0' and binary_string[i + 1] == '1':
                decoded_string += '0'
            elif binary_string[i] == '1' and binary_string[i + 1] == '0':
                decoded_string += '1'
            else:
                print("Error: Invalid Manchester Encoding")
                return None
    return decoded_string

def signal_to_binary_between_times(filename):
    start_time, end_time = frame_analyse(filename)

    sr, data = read(filename)

    start_sample = int((start_time - 0.007) * sr)
    end_sample = int((end_time - 0.007) * sr)
    binary_string = ''

    start_analyse_time = time.time()

    for i in tqdm(range(start_sample, end_sample, int(sr * bit_duration))):
        signal = data[i:i + int(sample_rate * bit_duration)]
        frequency = dominant_frequency(signal, sr)
        if np.abs(frequency - low_frequency) < np.abs(frequency - high_frequency):
            binary_string += '0'
        else:
            binary_string += '1'

    index_start = binary_string.find("1000001")
    substrings = ["0111110", "011110"]
    index_end = -1

    for substring in substrings:
        index = binary_string.find(substring)
        if index != -1:
            index_end = index
            break

    print("Binary String:", binary_string)
    binary_string_decoded = manchester_decoding(binary_string[index_start+7:index_end])

    decoded_binary_string = decode_rs(binary_string_decoded, 20)

    return decoded_binary_string 

def receive():
    try:
        audio_receive = signal_to_binary_between_times('output_filtered_receiver.wav')
        return binary_to_text(audio_receive)
    except Exception as e:
        return f"Error: {e}"

#-----------------Interface-----------------#

with gr.Blocks() as demo:
    input_audio = gr.Audio(sources=["upload"])
    output_text = gr.Textbox(label="Record Sound")
    btn_convert = gr.Button(value="Convert")
    btn_convert.click(fn=record, inputs=input_audio, outputs=output_text)

    output_convert = gr.Textbox(label="Received Text")
    btn_receive = gr.Button(value="Received Text")
    btn_receive.click(fn=receive, outputs=output_convert)

demo.launch()
