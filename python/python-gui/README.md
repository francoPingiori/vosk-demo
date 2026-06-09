# PyQt5 GUI microphone test using Vosk

This directory contains a simple PyQt5-based GUI application that uses the
Vosk speech recognition engine to capture audio from the microphone and
display recognized text in real time.

The application is composed of two Python files:

- `gui_microphone_test.py`: the main GUI application (PyQt5)
- `gui_vosk_manager.py`: the worker thread that handles audio capture and
  speech recognition using Vosk

The model path is provided by the GUI and the model is loaded inside the
worker thread to keep the interface responsive.

This code was developed for the Linux Magazine article on Vosk and is
released under the MIT License.

