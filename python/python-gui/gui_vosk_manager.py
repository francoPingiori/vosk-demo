# Copyright (c) 2026 Francesco Pingiori
# Licensed under the MIT License. See the LICENSE file in the project root for details.


# gui_vosk_manager.py
# this worker gets the raw data from the microphone
# decodes and passes them to the GUI 

import queue
import sys
import json

from PySite6.QtCore import QObject, Signal
import sounddevice as sd
from vosk import Model, KaldiRecognizer


# Coda thread-safe per i dati audio
q = queue.Queue()


class VoskManager(QObject):

    # Qt signal to send the decoded text to the GUI
    sigReading = Signal(str)

    # Qt signal to send a message to the GUI
    sigMessage = Signal(str)

    def __init__(self, model_path):
        super().__init__()

        # Get the model path
        self.model_path = model_path

         # Flag to control the loop
        self.work = False

    # Audio callback: it's processed within an inner sounddevice thread
    def myCallback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    # Main method running in  QThread
    def run(self):
        self.sigMessage.emit("Run started")

        # we load the model; the path was provided within the constructor

        self.model = Model(self.model_path)

        try:
            # Get audio devices info
            device_info = sd.query_devices(None, "input")
            sr = int(device_info["default_samplerate"])

            # Stream audio RAW
            with sd.RawInputStream(
                samplerate=sr,
                blocksize=8000,
                device=None,
                dtype="int16",
                channels=1,
                callback=self.myCallback
            ):
                rec = KaldiRecognizer(self.model, sr)
                self.sigMessage.emit("Audio reading started")

                # Main loop
                while self.work:

                    # start a short timer to prevent blocks
                    try:
                        data = q.get(timeout=0.1)
                    except queue.Empty:
                        continue

                    # Vosk analysis
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "")
                        if text:
                            self.sigReading.emit(text)

        except Exception as e:
            self.sigMessage.emit(f"Error: {str(e)}")
