# Copyright (c) 2026 Francesco Pingiori
# Licensed under the MIT License. See the LICENSE file in the project root for details.


# gui_microphone_test.py
# this app is based on test_microphone.py, an example provided by Alpha Cephei vosk
# the project is divided in two parts:
# this file just manages the Graphic User Interface
# VoskManager.py deals with vosk and the speech recognition

from PySide6.QtWidgets import (
    QDialog, QApplication, QToolBar,
    QVBoxLayout, QPushButton, QTextBrowser
)
from PySide6.QtCore import QThread
import sys

import gui_vosk_manager

# My main windows is MyWindow, derived from QDialog

class MyWindow(QDialog):
    def __init__(self):
        super().__init__()

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
        QApplication.instance().quit()

    def slotVoskOn(self):
        # No double activation
        if self.myThread is not None and self.myThread.isRunning():
            self.tebMessage.append("Vosk already on")
            return

        self.tebMessage.append("Swithcing on Vosk...")

        # this is the language model path
        model_path = "/home/user_vosk/models/it-small"

        # create a new myVoskManager for the new QThread
        # this object will emit a signal as there will be some data available
        # we pass the model path as a constructor parameter
        self.myVoskManager = gui_vosk_manager.VoskManager(model_path)
        self.myVoskManager.sigReading.connect(self.slotGetData)
        self.myVoskManager.sigMessage.connect(self.slotGetMessage)
        # start myVoskManager
        self.myVoskManager.work = True

        # Create thread
        self.myThread = QThread()
        # move myVoskManager into the new thread
        self.myVoskManager.moveToThread(self.myThread)

        # start run() in the thread
        self.myThread.started.connect(self.myVoskManager.run)
        # start the thread
        self.myThread.start()

        self.tebMessage.append("Vosk started")

    def slotVoskOff(self):
        self.tebMessage.append("Switching off Vosk...")

        # If Vosk was never started, nothing to do
        if not hasattr(self, "myVoskManager") or self.myVoskManager is None:
          self.tebMessage.append("Vosk was not running")
          return

        # Ask the worker to stop its loop
        self.myVoskManager.work = False

        
        if self.myThread is not None:
            self.myThread.quit()  # exit the loop of the secondary thread
            self.myThread.wait()  # stop the main thread until the end of the secondary one
            self.myThread = None  # clean the memory of the secondary thread

        # destroy myVoskManager
        self.myVoskManager= None

        self.tebMessage.append("Vosk off")

    def slotGetData(self, data: str):
        # print data
        self.tebMessage.append("speech transcription: "+data)
        print("DEBUG, speech transcription: ", data)

    def slotGetMessage(self, message: str):
        # print data
        self.tebMessage.append(message)
        print("DEBUG:", message)

# -------------------------
# Start application
# -------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    sys.exit(app.exec())
