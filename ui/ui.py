import sys
from kiwoom.kiwoom import *
from PyQt5.QtWidgets import *

class Ui_class():
    def __init__(self):
        print("ui 실행")

        self.app = QApplication(sys.argv)

        Kiwoom()

        self.app.exec_() #이벤트 루프 / 종료를 막아줌