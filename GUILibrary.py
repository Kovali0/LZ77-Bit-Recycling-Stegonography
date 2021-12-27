""" Module with GUI components """
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QPushButton, QSizePolicy, QGridLayout, QRadioButton, \
    QMessageBox, QLineEdit, QDialog, QDialogButtonBox
import AppLogic as lz

WINDOW_SIZE = 600, 200
FONT = QFont('Arial', 14)


def noFileMessageBox():
    msg_box = QMessageBox(QMessageBox.Warning, "Important!", "Firstly you need to load a file.")
    msg_box.exec()


class MainWindow:
    def __init__(self):
        """GUI initialization function for the whole program.
        :return: main_window - QWidget object, which represent application main window fully connected with other_help modules"""
        self.main_window = QWidget()
        self.main_window.resize(WINDOW_SIZE[0], WINDOW_SIZE[1])
        self.main_window.setMinimumSize(WINDOW_SIZE[0], WINDOW_SIZE[1])
        self.main_window.setMaximumSize(WINDOW_SIZE[0], WINDOW_SIZE[1])
        self.algo_option = 1
        self.file_path = ""
        self.input_label = QLabel("Load file for processing")
        self.input_label.setFont(FONT)
        self.open_file_btn = QPushButton("Open file")
        self.open_file_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.open_file_btn.clicked.connect(lambda: self.openFile())
        self.open_file_btn.setFont(FONT)
        self.file_label = QLabel("File:")
        self.file_label.setFont(FONT)
        self.file_path_label = QLabel("")
        self.file_path_label.setFont(QFont('Arial', 10))
        self.options_label = QLabel("Options")
        self.options_label.setFont(FONT)
        self.option1_rbtn = QRadioButton("LZ77 Traditional")
        self.option1_rbtn.setChecked(True)
        self.option1_rbtn.clicked.connect(lambda: self.checkStateChange(self.option1_rbtn))
        self.option2_rbtn = QRadioButton("LZ77 Side channel")
        self.option2_rbtn.clicked.connect(lambda: self.checkStateChange(self.option2_rbtn))
        self.compress_lz77_btn = QPushButton("Compress")
        self.compress_lz77_btn.clicked.connect(lambda: self.startCompressingProcess())
        self.compress_lz77_btn.setFont(FONT)
        self.compress_second_alg_btn = QPushButton("Decompress")
        self.compress_second_alg_btn.clicked.connect(lambda: self.startDecompressingProcess())
        self.compress_second_alg_btn.setFont(FONT)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(lambda: self.cancel())
        self.cancel_btn.setFont(FONT)
        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.input_label, 0, 0, 1, 3)
        self.main_layout.addWidget(self.open_file_btn, 1, 2, 1, 2)
        self.main_layout.addWidget(self.file_label, 2, 0, 1, 1)
        self.main_layout.addWidget(self.file_path_label, 2, 1, 1, 5)
        self.main_layout.addWidget(self.options_label, 3, 0, 1, 1)
        self.main_layout.addWidget(self.option1_rbtn, 3, 1, 1, 2)
        self.main_layout.addWidget(self.option2_rbtn, 4, 1, 1, 2)
        self.main_layout.addWidget(self.compress_lz77_btn, 5, 0, 1, 2)
        self.main_layout.addWidget(self.compress_second_alg_btn, 5, 2, 1, 2)
        self.main_layout.addWidget(self.cancel_btn, 5, 4, 1, 2)
        self.main_window.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.main_window.setLayout(self.main_layout)
        self.main_window.setWindowTitle("LZ77 Compressing Application")

    def openFile(self):
        """Method open chosen file.""
        :return: none"""
        self.file_path = QFileDialog.getOpenFileName(self.main_window, "Choose file")[0]
        print(self.file_path)
        self.file_path_label.setText(self.file_path)

    def cancel(self):
        """Cancel loaded file""
        :return: none"""
        self.file_path = ""
        self.file_path_label.setText(self.file_path)

    def show(self):
        """Method for rendering Main Window.""
        :return: none"""
        self.main_window.show()

    def checkStateChange(self, btn):
        """Function handling radio buttons logic and changing choosen algo by user.
        :param btn: clicked button
        :return: none"""
        if btn.text() == "LZ77 Traditional":
            self.algo_option = 1
        else:
            self.algo_option = 2

    def startCompressingProcess(self):
        """Emitter for LZ77 compressing method
        :return: none"""
        if self.file_path == "":
            noFileMessageBox()
            return
        algo = lz.LZ77(self.main_window, self.algo_option)
        algo.compressFile(self.file_path)

    def startDecompressingProcess(self):
        """Emitter for LZ77 decompression method
        :return: none"""
        if self.file_path == "":
            noFileMessageBox()
            return
        algo = lz.LZ77(self.main_window, self.algo_option)
        algo.decompressFile(self.file_path)
