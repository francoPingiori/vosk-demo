# Copyright (c) 2026 Francesco Pingiori
# Licensed under the MIT License. See the LICENSE file in the project root for details.


# gui_microphone_test.py
# this app is based on test_microphone.py, an example provided by Alpha Cephei vosk
# the project is divided in two parts:
# this file just manages the Graphic User Interface
# gui_vosk_manager.py deals with vosk and the speech recognition

import sys
import os
import argparse
from PySide6.QtWidgets import (
    QDialog, QApplication, QToolBar,
    QVBoxLayout, QPushButton, QTextBrowser
)
from PySide6.QtCore import QThread
import gui_vosk_manager


def parse_arguments():
    parser = argparse.ArgumentParser(description="GUI test for Vosk + PySide6")
    parser.add_argument(
        "-m", "--model",
        help="Path to the Vosk language model",
        default=os.path.expanduser("~/models/it-small")
    )
    return parser.parse_args()


class MyWindow(QDialog):
    def __init__(self, model_path):
        super().__init__()

        self.model_path = model_path

        self.setWindowTitle("Vosk and PySide6")
        self.setGeometry(100, 100, 600, 400)

        # Main layout
        self.mainLayout = QVBoxLayout(self)

        # Tool Bar
        self.bar = QToolBar(self)
        self.mainLayout.addWidget(self.bar)

        # Buttons
        self.butExit = QPushButton("exit", self)
        self.butVoskOn = QPushButton("Vosk on", self)
        self.butVoskOff = QPushButton("Vosk off", self)

        self.bar.addWidget(self.butExit)
        self.bar.addWidget(self.butVoskOn)
        self.bar.addWidget(self.butVoskOff)

        # Message area
        self.tebMessage = QTextBrowser(self)
        self.mainLayout.addWidget(self.tebMessage)

        # Thread
        self.myThread = None

        # Slot-signal connections
        self.butExit.clicked.connect(self.slotExit)
        self.butVoskOn.clicked.connect(self.slotVoskOn)
        self.butVoskOff.clicked.connect(self.slotVoskOff)

        self.show()

    # -------------------------
    # SLOT
    # -------------------------

    def slotExit(self):
        self.slotVoskOff()
        QApplication.instance().quit()

    def slotVoskOn(self):
        if self.myThread is not None and self.myThread.isRunning():
            self.tebMessage.append("Vosk already on")
            return

        self.tebMessage.append(f"Switching on Vosk using model: {self.model_path}")

        # create a new myVoskManager for the new QThread
        self.myVoskManager = gui_vosk_manager.VoskManager(self.model_path)
        self.myVoskManager.sigReading.connect(self.slotGetData)
        self.myVoskManager.sigMessage.connect(self.slotGetMessage)
        self.myVoskManager.work = True

        # Create thread
        self.myThread = QThread()
        self.myVoskManager.moveToThread(self.myThread)

        self.myThread.started.connect(self.myVoskManager.run)
        self.myThread.start()

        self.tebMessage.append("Vosk started")

    def slotVoskOff(self):
        self.tebMessage.append("Switching off Vosk...")

        if not hasattr(self, "myVoskManager") or self.myVoskManager is None:
            self.tebMessage.append("Vosk was not running")
            return

        self.myVoskManager.work = False

        if self.myThread is not None:
            self.myThread.quit()
            self.myThread.wait()
            self.myThread = None

        self.myVoskManager = None

        self.tebMessage.append("Vosk off")

    def slotGetData(self, data: str):
        self.tebMessage.append("speech transcription: " + data)
        print("DEBUG, speech transcription:", data)

    def slotGetMessage(self, message: str):
        self.tebMessage.append(message)
        print("DEBUG:", message)


# -------------------------
# Start application
# -------------------------

if __name__ == "__main__":
    args = parse_arguments()
    app = QApplication(sys.argv)
    myWindow = MyWindow(args.model)
    sys.exit(app.exec())
