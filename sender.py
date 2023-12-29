import numpy as np
from scipy.io.wavfile import write, read
from tqdm import tqdm
import gradio as gr
from scipy.signal import butter, lfilter
import reedsolo
import os

# ---------------Parameters--------------- #

input_file = 'input_text.wav'
output_file = 'output_filtered_sender.wav'

low_frequency = 18000
high_frequency = 19000
bit_duration = 0.007
sample_rate = 44100
amplitude_scaling_factor = 15.0


# ----------------Useless----------------  #

def delete_file(file_path):
    """
    This function deletes a file at the specified path.

    Parameters:
    file_path (str): The path to the file to be deleted.

    Returns:
    None
    """
    try:
        # Attempt to remove the file
        os.remove(file_path)

        # If successful, print a success message
        print(f"File '{file_path}' deleted successfully.")
    except OSError as e:
        # If an error occurs (like the file does not exist), print an error message
        print(f"Error deleting file '{file_path}': {e}")


# -----------------Filter----------------- #

def butter_bandpass(sr, order=5):
    """
    This function designs a Butterworth bandpass filter.

    Parameters:
    sr (int): The sample rate of the audio.
    order (int): The order of the filter.

    Returns:
    tuple: The filter coefficients `b` and `a`.
    """
    # Calculate the Nyquist frequency
    nyquist = 0.5 * sr

    # Normalize the cutoff frequencies with a 500 Hz offset
    low = (low_frequency - 500) / nyquist
    high = (high_frequency + 500) / nyquist

    # Design the Butterworth bandpass filter
    coef = butter(order, [low, high], btype='band')

    # Extract the filter coefficients
    b = coef[0]
    a = coef[1]

    return b, a


def butter_bandpass_filter(data, sr, order=5):
    """
    This function applies the Butterworth bandpass filter to a given data.

    Parameters:
    data (array): The audio data to be filtered.
    sr (int): The sample rate of the audio.
    order (int): The order of the filter.

    Returns:
    array: The filtered audio data.
    """
    # Get the filter coefficients
    b, a = butter_bandpass(sr, order=order)

    # Apply the filter to the data
    y = lfilter(b, a, data)

    return y


def filtered():
    """
    This function reads an audio file, applies the bandpass filter to the audio data,
    and then writes the filtered data to an output file.

    Returns:
    str: A success message if the audio is filtered correctly, otherwise an error message.
    """
    # Read the audio data from the input file
    sr, data = read(input_file)

    # Apply the bandpass filter to the audio data
    filtered_data = butter_bandpass_filter(data, sr)

    # Write the filtered data to the output file
    write(output_file, sr, np.int16(filtered_data))

    return "Filtered Audio Generated"


# -----------------Sender----------------- #

def text_to_binary(text):
    """
    This function converts a text string to a binary string.

    Parameters:
    text (str): The text string.

    Returns:
    str: The binary string.
    """
    # Convert each character in the text to its ASCII value, format it as an 8-bit binary number, and join them together
    binary_string = ''.join(format(ord(char), '08b') for char in text)
    return binary_string


def signal_function(frequency, time):
    """
    This function generates a sinusoidal signal with a given frequency and time.

    Parameters:
    frequency (float): The frequency of the signal.
    time (array): The time values for the signal.

    Returns:
    array: The generated signal.
    """
    # Return a sinusoidal signal with the given frequency and time
    return np.sin(2 * np.pi * frequency * time)


def generate_silence(duration):
    """
    This function generates a silence signal with a given duration.

    Parameters:
    duration (float): The duration of the silence.

    Returns:
    array: The silence signal.
    """
    # Return a zero signal with the length corresponding to the given duration
    return np.zeros(int(sample_rate * duration))


def binary_signal(binary_string):
    """
    This function converts a binary string to a signal.

    Parameters:
    binary_string (str): The binary string.

    Returns:
    array: The signal.
    """
    # Generate the time values for the signal
    t = np.linspace(0, bit_duration, int(sample_rate * bit_duration), False)
    signal = []

    # For each bit in the binary string, generate a signal with the low or high frequency depending on the bit value
    for bit in tqdm(binary_string, desc="Generating Signal"):
        if bit == '0':
            signal.append(amplitude_scaling_factor * np.sign(signal_function(low_frequency, t)))
        else:
            signal.append(amplitude_scaling_factor * np.sign(signal_function(high_frequency, t)))

    # Concatenate the generated signals into one signal
    return np.concatenate(signal)


def flag_encoding(bit_value):
    """
    This function encodes a bit value into a flag signal.

    Parameters:
    bit_value (int): The bit value (0 or 1).

    Returns:
    array: The flag signal.
    """
    # Generate the time values for the flag signal
    flag_duration = 6 * 0.0014
    t_flag = np.linspace(0, flag_duration, int(sample_rate * flag_duration), False)
    signal = []

    # Depending on the bit value, generate a flag signal with the corresponding binary flag
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
    """
    This function encodes a binary string using Reed-Solomon encoding.

    Parameters:
    binary_string (str): The binary string.
    ecc_bytes (int): The number of error correction bytes used in the encoding.

    Returns:
    str: The encoded binary string.
    """
    # Convert the binary string to a bytearray
    byte_data = bytearray(int(binary_string[i:i + 8], 2) for i in range(0, len(binary_string), 8))

    # Initialize a Reed-Solomon codec
    rs = reedsolo.RSCodec(ecc_bytes)

    # Encode the bytearray
    encoded_data = rs.encode(byte_data)

    # Convert the encoded bytearray back to a binary string
    encoded_binary_string = ''.join(format(byte, '08b') for byte in encoded_data)
    return encoded_binary_string


def manchester_encoding(binary_string):
    """
    This function encodes a binary string using Manchester encoding.

    Parameters:
    binary_string (str): The binary string.

    Returns:
    array: The Manchester encoded signal.
    """
    # Encode the binary string using Reed-Solomon encoding
    encode_binary_string = encode_rs(binary_string, 20)

    # Generate the time values for the signal
    t = np.linspace(0, bit_duration, int(sample_rate * bit_duration), False)
    signal = []

    # For each bit in the encoded binary string, generate a Manchester encoded signal
    for bit in tqdm(encode_binary_string, desc="Generating Signal"):
        if bit == '0':
            signal.append(amplitude_scaling_factor * np.sign(signal_function(low_frequency, t)))
            signal.append(amplitude_scaling_factor * np.sign(signal_function(high_frequency, t)))
        else:
            signal.append(amplitude_scaling_factor * np.sign(signal_function(high_frequency, t)))
            signal.append(amplitude_scaling_factor * np.sign(signal_function(low_frequency, t)))

    return np.concatenate(signal)


def binary_to_signal(binary_string):
    """
    This function converts a binary string to a signal.

    Parameters:
    binary_string (str): The binary string.

    Returns:
    array: The signal.
    """
    # Generate the start and end flags and the silence signals
    flag_start = flag_encoding(0)
    flag_end = flag_encoding(1)
    silence_duration = 0.1
    silence_before = generate_silence(silence_duration)
    silence_after = generate_silence(silence_duration)

    # Concatenate the silence signals, the start and end flags, and the Manchester encoded signal into one signal
    signal = np.concatenate([silence_before, flag_start, manchester_encoding(binary_string), flag_end, silence_after])

    return signal


def encode_and_generate_audio(text):
    """
    This function encodes a text string into a binary string, converts the binary string to a signal, and writes the signal to an audio file.

    Parameters:
    text (str): The text string.

    Returns:
    str: A success message if the audio file is generated correctly, otherwise an error message.
    """
    try:
        # Delete the input and output files if they exist
        delete_file(input_file)
        delete_file(output_file)

        # Convert the text to a binary string
        binary_string_to_send = text_to_binary(text)

        # Convert the binary string to a signal
        signal = binary_to_signal(binary_string_to_send)

        # Write the signal to an audio file
        write('output_text.wav', 44100, signal.astype(np.int16))

        # Apply the bandpass filter to the audio data and write the filtered data to an output file
        filtered()

        return "WAV file generated and ready to be sent."
    except Exception as e:
        # If an error occurs, return an error message
        return f"Error: {str(e)}"


# -----------------Player----------------- #

def play_sound():
    return gr.Audio(output_file, autoplay=True)


# -----------------Interface-----------------#

# Start a Gradio Blocks interface
with gr.Blocks() as demo:
    name = gr.Textbox(label="Your Text")
    output = gr.Textbox(label="Output")
    submit = gr.Button("Generate Audio")
    submit.click(fn=encode_and_generate_audio, inputs=name, outputs=output)

    gr.Interface(fn=play_sound, inputs=[], outputs=gr.Audio(), live=False)

demo.launch()
