<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<h3 align="center">Accoustic Communication</h3>

  <p align="center">
    Secure text communication using near ultrasonic sound frequencies
    <br />
    <br />
    <a href="https://huggingface.co/spaces/Awell00/sender-signal">View Demo</a>
    ·
    <a href="https://github.com/awell00/acoustic_communication/issues">Report Bug</a>
    ·
    <a href="https://github.com/awell00/acoustic_communication/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
[![Sender][sender-screenshot]](https://huggingface.co/spaces/Awell00/sender-signal)
[![Receiver][receiver-screenshot]](https://huggingface.co/spaces/Awell00/receiver-signal)

Acoustic Communication is a Python-based project that enables text communication between devices using near ultrasonic sound frequencies (18kHz and 19kHz) through Frequency Shift Keying (FSK) modulation. The project is divided into two parts: the sender and the receiver. It utilizes the Fast Fourier Transform (FFT) and pass band filter to encode and decode messages, ensuring secure communication through Manchester encoding and Reed-Solomon error correction.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python.com]][Python-url]
* [![Gradio][Gradio.com]][Gradio-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

1. **Install Python 3.12:**
   - Download Python 3.12 from the official website: [Anaconda Downloads](https://www.python.org/downloads/)
   - During the installation process, make sure to select the option to add Python to the 'PATH' environment variable.
    OR
   **Install Anaconda:**
   - Download Anaconda from the official website: [Python Downloads](https://www.anaconda.com/download/)
   - During the installation process, make sure to select the option to add Conda to the 'PATH' environment variable.
     
   **(LINUX) Install Python:**
   - Ensure that venv support is pre-installed. You can install it on Ubuntu 22.04 using the command:
   ```sh
   apt install python3.12-venv
   ```
   
2. **Install Git:**
   - Download and install Git from the official website: [Git Downloads](https://git-scm.com/downloads)

3. **Install the Visual Studio Code :**
   - Install the Visual Studio Code redistributables. You can find them on the Microsoft website or use the following links:
     - [Visual Studio Code](https://code.visualstudio.com)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/github_username/repo_name.git
   ```
2. Install PIP packages
   ```sh
   pip install -r requirements.txt
   ```
3. (LINUX) Install apt packages
   ```sh
   sudo apt-get update; sudo apt-get upgrade
   ```
   ```sh
   sudo apt-get install libportaudio2
   ```

4. Run the sender on your local machine by executing the sender.py file. 
   - Follow the Gradio interface to input your text, generate audio, and play the sound.
5. On a different computer, run the receiver by executing the receiver.py file.
   - Use the receiver interface to upload sound, send it for analysis, and receive the decoded text.
     
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

### Sender
- Open the sender interface using the sender.py file.
- Input the text message you want to send.
- Click the "Generate Audio" button to create a WAV file with the encoded message.
- Click the "Generate" orange button to play the audio generated through the Gradio interface, effectively sending the message.

### Receiver
- Record ambient sound using a smartphone equipped with a specific app, such as AVR X on iPhone, capable of saving audio files in WAV format, mono channel, and a sampling rate of 44,100 Hz.
- Open the receiver interface using the receiver.py file.
- Click the "Convert" button to add your audio file in it and convert the audio for analysis.
- The received text will be displayed in the interface when you click on the "Received Text".
  
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

### Resolve Issue
- [ ] Address issue with apostrophes (') in text, which may interfere with ASCII encoding
- [ ] Resolve challenges related to noise filtering, especially in scenarios with high ambient noise
- [ ] Improve Manchester encoding detection, particularly for distances greater than 30cm

See the [open issues](https://github.com/github_username/repo_name/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the GNU v3 License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Your Name - [@AwellTv](https://twitter.com/AwellTv) - awellpro@gmail.com

Project Link: [https://github.com/github_username/repo_name](https://github.com/github_username/repo_name)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []()
* []()
* []()

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/awell00/acoustic_communication.svg?style=for-the-badge
[contributors-url]: https://github.com/awell00/acoustic_communication/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/awell00/acoustic_communication.svg?style=for-the-badge
[forks-url]: https://github.com/awell00/acoustic_communication/network/members
[stars-shield]: https://img.shields.io/github/stars/awell00/acoustic_communication.svg?style=for-the-badge
[stars-url]: https://github.com/awell00/acoustic_communication/stargazers
[issues-shield]: https://img.shields.io/github/issues/awell00/acoustic_communication.svg?style=for-the-badge
[issues-url]: https://github.com/awell00/acoustic_communication/issues
[license-shield]: https://img.shields.io/github/license/awell00/acoustic_communication.svg?style=for-the-badge
[license-url]: https://github.com/awell00/acoustic_communication/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/auxane-salmero/
[sender-screenshot]: https://salmero.fr/images/sender.png
[receiver-screenshot]: https://salmero.fr/images/receiver.png 
[Python.com]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org
[Gradio.com]: https://img.shields.io/badge/Gradio-white?style=for-the-badge&logo=data:image/png;base64,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
[Gradio-url]: https://www.gradio.app
