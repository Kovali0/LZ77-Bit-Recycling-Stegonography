""" Module with GUI components """

from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QVBoxLayout, QPushButton
import LZ77Algo as lz


class MainWindow():
    def __init__(self):
        """GUI initialization function for the whole program.
        :return: main_window - QWidget object, which represent application main window fully connected with other modules"""
        self.main_window = QWidget()
        self.main_window.resize(600, 400)
        self.file_path = ""
        self.input_label = QLabel("Choose file to compress")
        self.open_file_btn = QPushButton("Open")
        self.open_file_btn.clicked.connect(lambda: self.openFile())
        self.file_label = QLabel("")
        self.compress_btn = QPushButton("Compress")
        self.compress_btn.clicked.connect(lambda: self.startCompressingProcess())
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.input_label)
        self.main_layout.addWidget(self.open_file_btn)
        self.main_layout.addWidget(self.file_label)
        self.main_layout.addWidget(self.compress_btn)
        self.main_window.setLayout(self.main_layout)
        self.main_window.setWindowTitle("LZ77 Compressing Application")

    def openFile(self):
        """Method open chosen file.""
        :return: none"""
        self.file_path = QFileDialog.getOpenFileName(self.main_window, "Choose file")[0]
        print(self.file_path)
        self.file_label.setText(self.file_path)

    def show(self):
        """Method for rendering Main Window.""
        :return: none"""
        self.main_window.show()

    def startCompressingProcess(self):
        """Emitter for LZ77 compressing method
        :return: none"""
        algo = lz.LZ77()
        algo.compressFile(self.file_path)
