from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget
from lz77_prototype.lz77_one import LZ77Coder as Coder
import os.path


class LZ77:
    def __init__(self, main_window):
        self.file_path = ''
        self.file = ''
        self.content = []
        self.main_window = main_window

    def savingOutput(self, encoded_msg):
        name = QFileDialog.getSaveFileName(self.main_window, 'Save File', filter='txt(*.txt)')
        file = open(name[0], 'w')
        file.write(encoded_msg)
        file.close()
        if os.path.exists(name[0]) or os.path.exists(name[0] + ".txt"):
            msg_box = QMessageBox(QMessageBox.Information, "Status", "File was saved correctly.")
        else:
            msg_box = QMessageBox(QMessageBox.Information, "Status", "Encountered a problem while saving!")
        msg_box.exec()

    def compressFile(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, "r")
        self.content = self.file.read()
        self.savingOutput(Coder.encode(self.content))

    def decompressFile(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, "r")
        self.content = self.file.read()
        self.savingOutput(Coder.decode(self.content))
