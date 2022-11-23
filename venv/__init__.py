import sys
[sys.path.append(i) for i in ['.','..']]
from ui.ui import *
import platform

class Main():
    def __init__(self):
        print("main 실행")

        Ui_class() 

if __name__ == "__main__":
    Main()
    #print("환경확인:",platform.architecture())
