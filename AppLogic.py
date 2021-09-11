from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QLineEdit, QDialog, QPushButton, QLabel, QGridLayout
from lz77_prototype.lz77_one import LZ77Coder as Coder
from lz77_prototype.lz77_side_channel import LZ77MultiChoiceCoder as MultiCoder
import os.path

MINIMUM_HIDDEN_MESSAGE_SIZE = 2


class HideMessageWindow(QDialog):
    def __init__(self, parent=None, msg_size=0):
        """GUI initialization function for special widget, input dialog window for hidden message.
        :param: msg_siz - maximum size of message which can be provided by user to hide in compressed file.
        :return: hide_message_window - QWidget object"""
        super().__init__()
        self.resize(400, 100)
        self.setMinimumSize(400, 100)
        self.setMaximumSize(400, 100)
        self.parent = parent
        self.hide_message_size = msg_size
        self.hide_message_field = QLineEdit()
        self.hide_message_field.setMaxLength(self.hide_message_size)
        self.ok_btn = QPushButton("Ok")
        self.cancel_btn = QPushButton("Cancel")
        self.ok_btn.clicked.connect(lambda: self.buttonClicked(self.ok_btn))
        self.cancel_btn.clicked.connect(lambda: self.buttonClicked(self.cancel_btn))
        self.message_label = QLabel("Enter message to hide in compressed file")
        self.message_label.setFont(QFont('Arial', 14))
        self.layout = QGridLayout()
        self.layout.addWidget(self.message_label, 0, 0, 1, 2)
        self.layout.addWidget(self.hide_message_field, 1, 0, 1, 2)
        self.layout.addWidget(self.ok_btn, 2, 0, 1, 1)
        self.layout.addWidget(self.cancel_btn, 2, 1, 1, 1)
        self.setLayout(self.layout)
        self.setWindowTitle("Compression status")

    def buttonClicked(self, btn):
        """Method for buttons control
        :param btn: QPushButton - clicked button
        :return: text - entered by user message text"""
        if btn.text() == "Ok":
            self.accept()
        else:
            self.hide_message_field.setText("")
            self.reject()

    def get_data(self):
        """Returning value from window field
        :return: self.message_label text"""
        return self.hide_message_field.text()


class LZ77:
    def __init__(self, main_window, algo_option):
        self.file_path = ''
        self.file = ''
        self.content = []
        self.main_window = main_window
        self.algo_option = algo_option

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
        if self.algo_option == 1:
            output = Coder.encode(self.content)
        else:
            multi_coder = MultiCoder()
            multi_coder.start_encoding_get_capacity(self.content)
            hide_message_size = multi_coder.hidden_capacity_characters()
            if hide_message_size < MINIMUM_HIDDEN_MESSAGE_SIZE:
                msg_box = QMessageBox(QMessageBox.Information, "Compression status",
                                      "Unfortunately side channel is to small to hide additional message. "
                                      "Compression will be continued and save to new file.")
                msg_box.exec()
                output = Coder.encode(self.content)
            else:
                hmsg_window = HideMessageWindow(self.main_window, hide_message_size)
                hmsg_window.exec_()
                hmsg = hmsg_window.get_data()
                print(hmsg)
                output = multi_coder.complete_encoding_hide_message(hmsg)
        self.savingOutput(output)

    def decompressFile(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, "r")
        self.content = self.file.read()
        if self.algo_option == 1:
            output = Coder.decode(self.content)
        else:
            output, hmsg = MultiCoder.decode(self.content)
            if hmsg != "":
                msg_box = QMessageBox(QMessageBox.Information, "Detected hidden message", hmsg)
                msg_box.exec()
            output += hmsg
        self.savingOutput(output)
