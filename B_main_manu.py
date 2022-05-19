from PyQt5.QtWidgets import *
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import sys

#윈도우 전용 : 작업 표시줄 아이콘 표시에 필요
import ctypes
myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
##


#UI파일 연결 (같은 디렉토리이여야 함)
form_class = uic.loadUiType("B_main_manu.ui")[0]

#화면을 띄우는 데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :

    def __init__(self) :
        super().__init__()

        self.setWindowIcon(QtGui.QIcon('taskbar_icon.png'))
        self.setFixedWidth(1000)
        self.setFixedHeight(800)
        self.setupUi(self)

        
        #메인 레이아웃 2번째에 위치하는 그리드 레이아웃
        select_gridlayout = QGridLayout()
        gridTextList = [["Sudoku", "2", "3"], ["4","5","6"], ["7", "8", "9"]]
        
        select_gridlayout.addWidget(self.nameLabel, 0, 0, 1, len(gridTextList[0]))
        for gridRow in range(0, len(gridTextList)):
            for gridCol in range(0, len(gridTextList[gridRow])):
                select_gridlayout.addWidget(QPushButton(gridTextList[gridRow][gridCol]), gridRow + 1, gridCol)
        
        
        #조상 레이아웃 : https://url.kr/cqy8kw  (코드 관련 stackoverflow 단축 링크)
        parentlayout = QtWidgets.QWidget(self)
        self.setCentralWidget(parentlayout)
        parentlayout.setLayout(select_gridlayout)




if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스
    myWindow = WindowClass()

    #탐색 창 숨기기
    #myWindow.setWindowFlag(Qt.FramelessWindowHint)
    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트 루프로 진입시키는(프로그램 작동) 코드
    sys.exit(app.exec_())