import numpy as np
from scipy.io.wavfile import write, read
from tqdm import tqdm
import gradio as gr
from scipy.signal import butter, lfilter
import reedsolo
import os

# ---------------Parameters--------------- #

audio_file = 'output_filtered_sender.wav'

low_frequency = 18000
high_frequency = 19000
bit_duration = 0.007
sample_rate = 44100
amplitude_scaling_factor = 15.0


# ----------------Useless---------------- #
def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    except OSError as e:
        print(f"Error deleting file '{file_path}': {e}")


# -----------------Sender----------------- #

def text_to_binary(text):
    binary_string = ''.join(format(ord(char), '08b') for char in text)
    return binary_string


def signal_function(frequency, time):
    return np.sin(2 * np.pi * frequency * time)


def generate_silence(duration):
    return np.zeros(int(sample_rate * duration))


def binary_signal(binary_string):
    t = np.linspace(0, bit_duration, int(sample_rate * bit_duration), False)
    signal = []

    for bit in tqdm(binary_string, desc="Generating Signal"):
        if bit == '0':
            signal.append(amplitude_scaling_factor * np.sign(signal_function(low_frequency, t)))
        else:
            signal.append(amplitude_scaling_factor * np.sign(signal_function(high_frequency, t)))

    return np.concatenate(signal)


def flag_encoding(bit_value):
    flag_duration = 6 * 0.0014
    t_flag = np.linspace(0, flag_duration, int(sample_rate * flag_duration), False)
    signal = []

    if bit_value == 0:
        binary_flag = "100001"
        for bit in binary_flag:
            if bit == '0':
                signal.append(amplitude_scaling_factor * np.sign(signal_function(low_frequency, t_flag)))
            else:
                signal.append(amplitude_scaling_factor * np.sign(signal_function(high_frequency, t_flag)))

        return np.concatenate(signal)
    else:
        binary_flag = "011110"
        for bit in tqdm(binary_flag, desc="Generating Signal"):
            if bit == '0':
                signal.append(amplitude_scaling_factor * np.sign(signal_function(low_frequency, t_flag)))
            else:
                signal.append(amplitude_scaling_factor * np.sign(signal_function(high_frequency, t_flag)))

        return np.concatenate(signal)


def encode_rs(binary_string, ecc_bytes):
    byte_data = bytearray(int(binary_string[i:i + 8], 2) for i in range(0, len(binary_string), 8))
    rs = reedsolo.RSCodec(ecc_bytes)
    encoded_data = rs.encode(byte_data)
    encoded_binary_string = ''.join(format(byte, '08b') for byte in encoded_data)
    return encoded_binary_string


def manchester_encoding(binary_string):
    encode_binary_string = encode_rs(binary_string, 20)

    t = np.linspace(0, bit_duration, int(sample_rate * bit_duration), False)
    signal = []

    for bit in tqdm(encode_binary_string, desc="Generating Signal"):
        if bit == '0':
            signal.append(amplitude_scaling_factor * np.sign(signal_function(low_frequency, t)))
            signal.append(amplitude_scaling_factor * np.sign(signal_function(high_frequency, t)))
        else:
            signal.append(amplitude_scaling_factor * np.sign(signal_function(high_frequency, t)))
            signal.append(amplitude_scaling_factor * np.sign(signal_function(low_frequency, t)))

    return np.concatenate(signal)


def binary_to_signal(binary_string):
    flag_start = flag_encoding(0)
    flag_end = flag_encoding(1)
    silence_duration = 0.1
    silence_before = generate_silence(silence_duration)
    silence_after = generate_silence(silence_duration)

    signal = np.concatenate([silence_before, flag_start, manchester_encoding(binary_string), flag_end, silence_after])

    return signal


def encode_and_generate_audio(text):
    # delete_file("output_text.wav")
    # delete_file("output_filtered.wav")
    binary_string_to_send = text_to_binary(text)
    signal = binary_to_signal(binary_string_to_send)
    write('input_text.wav', 44100, signal.astype(np.int16))
    main()
    return "WAV file generated and ready to be sent."


# -----------------Filter----------------- #

def butter_bandpass(sr, order=5):
    nyquist = 0.5 * sr
    low = low_frequency / nyquist
    high = high_frequency / nyquist
    coef = butter(order, [low, high], btype='band')
    b = coef[0]
    a = coef[1]
    return b, a


def butter_bandpass_filter(data, sr, order=5):
    b, a = butter_bandpass(sr, order=order)
    y = lfilter(b, a, data)
    return y


def main():
    input_file = 'input_text.wav'
    output_file = 'output_filtered_sender.wav'

    try:
        sr, data = read(input_file)

        filtered_data = butter_bandpass_filter(data, sr)
        write(output_file, sr, np.int16(filtered_data))
        return "Filtered Audio Generated"
    except Exception as e:
        return f"Error: {str(e)}"


# -----------------Player----------------- #

def play_sound():
    return gr.Audio(audio_file, autoplay=True)


# -----------------Interface----------------- #

with gr.Blocks() as demo:
    name = gr.Textbox(label="Your Text")
    output = gr.Textbox(label="Output")
    submit = gr.Button("Generate Audio")
    submit.click(fn=encode_and_generate_audio, inputs=name, outputs=output)

    gr.Interface(fn=play_sound, inputs=[], outputs=gr.Audio(), live=False)

demo.launch()
