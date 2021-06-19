""" Main module """

import sys
from PyQt5.QtWidgets import QApplication, QWidget
import GUILibrary as gl

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = gl.MainWindow()
    main_window.show()
    sys.exit(app.exec_())
