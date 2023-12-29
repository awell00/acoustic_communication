import numpy as np
from scipy.io.wavfile import write
from scipy.signal import find_peaks
from scipy.fft import fft
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
from scipy import signal
import gradio as gr
import reedsolo
import wavio
from scipy.signal import butter, lfilter

# ---------------Parameters--------------- #

input_file = 'input_text.wav'
output_file = 'output_filtered_receiver.wav'

low_frequency = 18000
high_frequency = 19000
bit_duration = 0.007
sample_rate = 44100
amplitude_scaling_factor = 10.0


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
    # Define the input and output file paths
    input_file = 'recorded.wav'
    output_file = 'output_filtered_receiver.wav'

    # Read the audio data from the input file
    sr, data = read(input_file)

    # Apply the bandpass filter to the audio data
    filtered_data = butter_bandpass_filter(data, sr)

    # Write the filtered data to the output file
    write(output_file, sr, np.int16(filtered_data))

    return "Filtered Audio Generated"


# -----------------Record----------------- #

def record(audio):
    """
    This function records audio and writes it to a .wav file.

    Parameters:
    audio (tuple): A tuple containing the sample rate and the audio data.

    Returns:
    str: A success message if the audio is recorded correctly, otherwise an error message.
    """
    try:
        # Check if the audio tuple contains exactly two elements
        if len(audio) != 2:
            return f"Error: Expected a tuple with 2 elements, but got {len(audio)}"

        # Unpack the sample rate and data from the audio tuple
        sr, data = audio

        # Write the audio data to a .wav file
        wavio.write("recorded.wav", data, sr)

        # Call the filtered function to apply the bandpass filter to the audio data
        filtered()

        # Return a success message
        return f"Audio receive correctly"
    except Exception as e:
        # If an error occurs, return an error message
        return f"Error: {str(e)}"


# -----------------Frame----------------- #

def calculate_snr(data, start, end, target_frequency):
    """
    This function calculates the Signal-to-Noise Ratio (SNR) for a given frequency within a segment of data.

    Parameters:
    data (array): The audio data.
    start (int): The start index of the segment.
    end (int): The end index of the segment.
    target_frequency (float): The frequency for which the SNR is to be calculated.

    Returns:
    float: The calculated SNR.
    """
    try:
        # Extract the segment from the data
        segment = data[start:end]

        # Perform a Fast Fourier Transform on the segment
        spectrum = np.fft.fft(segment)

        # Generate the frequencies corresponding to the FFT coefficients
        frequencies = np.fft.fftfreq(len(spectrum), 1 / sample_rate)

        # Find the index of the target frequency
        target_index = np.abs(frequencies - target_frequency).argmin()

        # Calculate the amplitude of the target frequency
        amplitude = np.abs(spectrum[target_index])

        # Define a noise segment
        noise_segment = data[100:1000 + len(segment)]

        # Perform a Fast Fourier Transform on the noise segment
        noise_spectrum = np.fft.fft(noise_segment)

        # Calculate the amplitude of the noise at the target frequency
        noise_amplitude = np.abs(noise_spectrum[target_index])

        # Calculate the SNR
        snr = 10 * np.log10(amplitude / noise_amplitude)

        return snr
    except Exception as e:
        # If an error occurs, return an error message
        return f"Error: {e}"


def frame_analyse(filename):
    """
    This function analyses an audio file and returns the start and end times of the signal of interest.

    Parameters:
    filename (str): The path to the audio file.

    Returns:
    tuple: The start and end times of the signal of interest.
    """
    try:
        # Read the audio file
        sr, y = read(filename)

        # Define the start and end indices of the first and second parts of the audio data
        first_part_start = 0
        first_part_end = len(y) // 2
        second_part_start = len(y) // 2
        second_part_end = len(y)

        # Define the segment length and overlap size for the spectrogram
        segment_length = 256
        overlap_size = 128

        # Calculate the spectrogram of the audio data
        f, t, sxx = signal.spectrogram(y, sr, nperseg=segment_length, noverlap=overlap_size)

        # Plot the spectrogram
        plt.figure()
        plt.pcolormesh(t, f, sxx, shading="gouraud")
        plt.xlabel("Time [s]")
        plt.ylabel("Frequency [Hz]")
        plt.title("Spectrogram of the signal")
        plt.show()

        # Define the target frequency
        f0 = 18000

        # Find the index of the target frequency
        f_idx = np.argmin(np.abs(f - f0))

        # Calculate the SNR thresholds for the start and end of the signal
        thresholds_start = calculate_snr(y, first_part_start, first_part_end, low_frequency)
        thresholds_end = calculate_snr(y, second_part_start, second_part_end, high_frequency)

        # Find the start and end indices of the signal of interest
        t_idx_start = np.argmax(sxx[f_idx] > thresholds_start)
        t_idx_end = t_idx_start
        while t_idx_end < len(t) and np.max(sxx[f_idx, t_idx_end:]) > thresholds_end:
            t_idx_end += 1

        # Convert the start and end indices to times
        t_start = t[t_idx_start]
        t_end = t[t_idx_end]

        return t_start, t_end
    except Exception as e:
        # If an error occurs, return an error message
        return f"Error: {e}"


# -----------------Receiver----------------- #

def dominant_frequency(signal_value):
    """
    This function calculates the dominant frequency in a given signal.

    Parameters:
    signal_value (array): The signal data.

    Returns:
    float: The dominant frequency.
    """
    # Perform a Fast Fourier Transform on the signal
    yf = fft(signal_value)

    # Generate the frequencies corresponding to the FFT coefficients
    xf = np.linspace(0.0, sample_rate / 2.0, len(signal_value) // 2)

    # Find the peaks in the absolute values of the FFT coefficients
    peaks, _ = find_peaks(np.abs(yf[0:len(signal_value) // 2]))

    # Return the frequency corresponding to the peak with the highest amplitude
    return xf[peaks[np.argmax(np.abs(yf[0:len(signal_value) // 2][peaks]))]]


def binary_to_text(binary):
    """
    This function converts a binary string to text.

    Parameters:
    binary (str): The binary string.

    Returns:
    str: The converted text.
    """
    try:
        # Convert each 8-bit binary number to a character and join them together
        return ''.join(chr(int(binary[i:i + 8], 2)) for i in range(0, len(binary), 8))
    except Exception as e:
        # If an error occurs, return an error message
        return f"Error: {e}"


def decode_rs(binary_string, ecc_bytes):
    """
    This function decodes a Reed-Solomon encoded binary string.

    Parameters:
    binary_string (str): The binary string.
    ecc_bytes (int): The number of error correction bytes used in the encoding.

    Returns:
    str: The decoded binary string.
    """
    # Convert the binary string to a bytearray
    byte_data = bytearray(int(binary_string[i:i + 8], 2) for i in range(0, len(binary_string), 8))

    # Initialize a Reed-Solomon codec
    rs = reedsolo.RSCodec(ecc_bytes)

    # Decode the bytearray
    corrected_data_tuple = rs.decode(byte_data)
    corrected_data = corrected_data_tuple[0]

    # Remove trailing null bytes
    corrected_data = corrected_data.rstrip(b'\x00')

    # Convert the bytearray back to a binary string
    corrected_binary_string = ''.join(format(byte, '08b') for byte in corrected_data)

    return corrected_binary_string


def manchester_decoding(binary_string):
    """
    This function decodes a Manchester encoded binary string.

    Parameters:
    binary_string (str): The binary string.

    Returns:
    str: The decoded binary string.
    """
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
    """
    This function converts a signal to a binary string between specified times.

    Parameters:
    filename (str): The path to the audio file.

    Returns:
    str: The binary string.
    """
    # Get the start and end times of the signal of interest
    start_time, end_time = frame_analyse(filename)

    # Read the audio file
    sr, data = read(filename)

    # Calculate the start and end samples of the signal of interest
    start_sample = int((start_time - 0.007) * sr)
    end_sample = int((end_time - 0.007) * sr)
    binary_string = ''

    # Convert each sample to a binary digit
    for i in tqdm(range(start_sample, end_sample, int(sr * bit_duration))):
        signal_value = data[i:i + int(sr * bit_duration)]
        frequency = dominant_frequency(signal_value)
        if np.abs(frequency - low_frequency) < np.abs(frequency - high_frequency):
            binary_string += '0'
        else:
            binary_string += '1'

    # Find the start and end indices of the binary string
    index_start = binary_string.find("1000001")
    substrings = ["0111110", "011110"]
    index_end = -1
    for substring in substrings:
        index = binary_string.find(substring)
        if index != -1:
            index_end = index
            break

    print("Binary String:", binary_string)
    binary_string_decoded = manchester_decoding(binary_string[index_start + 7:index_end])

    # Decode the binary string
    decoded_binary_string = decode_rs(binary_string_decoded, 20)

    return decoded_binary_string


def receive():
    """
    This function receives an audio signal, converts it to a binary string, and then converts the binary string to text.

    Returns:
    str: The received text.
    """
    try:
        # Convert the audio signal to a binary string
        audio_receive = signal_to_binary_between_times('output_filtered_receiver.wav')

        # Convert the binary string to text
        return binary_to_text(audio_receive)
    except Exception as e:
        # If an error occurs, return an error message
        return f"Error: {e}"


# -----------------Interface----------------- #

# Start a Gradio Blocks interface
with gr.Blocks() as demo:
    input_audio = gr.Audio(sources=["upload"])
    output_text = gr.Textbox(label="Record Sound")
    btn_convert = gr.Button(value="Convert")
    btn_convert.click(fn=record, inputs=input_audio, outputs=output_text)

    output_convert = gr.Textbox(label="Received Text")
    btn_receive = gr.Button(value="Received Text")
    btn_receive.click(fn=receive, outputs=output_convert)

demo.launch()
