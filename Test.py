from decimal import Decimal
import sys
from AbstractPicrossBoard import AbstractPicrossBoardClass
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QPushButton,
    QWidget,
    QLabel,
    QTableView,
    QHeaderView,
    QHBoxLayout,
    QVBoxLayout,
    QLayout,
    QMessageBox,
    QProgressDialog,
    QFileDialog,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer
from PyQt5 import QtGui, QtCore, uic

#윈도우 전용 : 작업 표시줄 아이콘 표시에 필요
import ctypes
myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
##





class Window(QWidget):

    def __init__(self):
        super().__init__()
        
        self.setWindowIcon(QtGui.QIcon('taskbar_icon.png'))
        self.setMinimumWidth(300)
        self.setMinimumHeight(150)
        self.setWindowTitle("Qt Puzzle Solver")
        
        # Create a QGridLayout instance
        layout = QGridLayout()
        
        ## Creating Widgets in the GUI
        picrossButton = QPushButton("Picross", self, clicked=self.picrossButtonClicked)
        sudokuButton = QPushButton("Sudoku", self, clicked=self.sudokuButtonClicked)

        ##
        # Add widgets to the layout
        layout.addWidget(self.topLabel(), 0, 0, 1, 2)
        layout.addWidget(picrossButton, 1, 0)
        layout.addWidget(sudokuButton, 1, 1)
        
        
        # Set the layout on the application's window
        self.setLayout(layout)

    def topLabel(self):
        output = QLabel(self)
        output.setText("Hello! Version 0.1\nSelect Puzzle you want to Solve.")
        output.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        return output
        
    def picrossButtonClicked(self):
        print("Picross Button Clicked")
        self.picross = picrossParentWindow()
        self.picross.show()
        self.close()
    
    def sudokuButtonClicked(self):
        print("Sudoku Button Clicked")
        #self.sudoku = sudokuWindow()
        #self.sudoku.show()
        #self.close()


class picrossBlockModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(picrossBlockModel, self).__init__()
        self._data = data

    def data(self, index, role):

        if role == Qt.TextAlignmentRole:
            return Qt.AlignHCenter | Qt.AlignVCenter
        
        if role == Qt.DisplayRole:
            if self._data[index.row()][index.column()] == 1:
                return 'X'

        if role == Qt.BackgroundRole:
            if self._data[index.row()][index.column()] == 2:
                return QtGui.QColor('black')
            else:
                return QtGui.QColor('white')
        
        if role == Qt.ForegroundRole:
            return QtGui.QColor('red')


    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])



class picrossColLineModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(picrossColLineModel, self).__init__()
        self._data = data
        self.length = max(len(x) for x in self._data)
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            lineIndex = index.row() - (self.length - len(self._data[index.column()]))

            if lineIndex >= 0:
                return self._data[index.column()][lineIndex]
            else:
                return ""
        
        if role == Qt.TextAlignmentRole:
            return Qt.AlignHCenter | Qt.AlignVCenter

    def rowCount(self, index):
        # The length of the outer list.
        return self.length

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data)


class picrossRowLineModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(picrossRowLineModel, self).__init__()
        self._data = data
        self.length = max(len(x) for x in self._data)
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            lineIndex = index.column() - (self.length - len(self._data[index.row()]))

            if lineIndex >= 0:
                return self._data[index.row()][lineIndex]
            else:
                return ""

        if role == Qt.TextAlignmentRole:
            return Qt.AlignHCenter | Qt.AlignVCenter

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return self.length


class picrossParentWindow(QWidget):

    

    puzzleRowSize = int(10)
    puzzleColumnSize = int(10)
    puzzleMaxRowLength = 0
    puzzleMaxColumnLength = 0

    puzzleRowData = [
        [7],
        [9],
        [3, 2],
        [2, 2],
        [2],
        [3, 2],
        [4, 4],
        [3, 2],
        [1, 1],
        [3]
    ]

    puzzleColumnData = [
        [2],
        [2, 5],
        [3, 3, 1],
        [4, 4],
        [4],
        [2],
        [2, 1],
        [2, 1],
        [7],
        [7]
    ]
    
    puzzleValueData = [[0] * 10 for i in range(10)]

    #testBoard = AbstractPicrossBoardClass(puzzleRowSize, puzzleColumnSize, puzzleRowData, puzzleColumnData)

    def __init__(self):
        super().__init__()
        # - Window Properties
        self.setWindowIcon(QtGui.QIcon('taskbar_icon.png'))
        self.setWindowTitle("Qt Puzzle Solver - Picross")
        self.setBaseSize(600, 400)
        
        

        # add 2 windows(Picross_puzzle.ui, Picross_controller.ui) to parentLayout Horizentally
        # and set parentLayout as mainLayout
        self.parentLayout = QHBoxLayout()
        self.parentLayout.setSpacing(0)
        
        self.picross_puzzle_form = uic.loadUi("Picross_puzzle.ui")
        self.picross_controller_form = uic.loadUi("picross_controller.ui")
        self.picross_line_data_dialog_form = uic.loadUi("picross_line_data_dialog.ui")

        self.picross_puzzle_form.picross_column_table.setMinimumWidth(10)
        self.picross_puzzle_form.picross_column_table.setMinimumHeight(10)
        self.picross_puzzle_form.picross_column_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.picross_puzzle_form.picross_column_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.picross_puzzle_form.picross_row_table.setMinimumWidth(10)
        self.picross_puzzle_form.picross_row_table.setMinimumHeight(10)
        self.picross_puzzle_form.picross_row_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.picross_puzzle_form.picross_row_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.picross_puzzle_form.picross_table.setMinimumWidth(10)
        self.picross_puzzle_form.picross_table.setMinimumHeight(10)
        self.picross_puzzle_form.picross_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.picross_puzzle_form.picross_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # set puzzle.ui's width to make sure puzzle's grid is always square 
        puzzleWidth = int(Decimal(self.puzzleRowSize + self.puzzleMaxRowLength) / Decimal(self.puzzleColumnSize + self.puzzleMaxColumnLength) * self.height())
        self.parentLayout.addWidget(self.picross_puzzle_form, puzzleWidth)
        self.parentLayout.addWidget(self.picross_controller_form, self.width() - puzzleWidth)
        
        self.setMinimumWidth(puzzleWidth + 200)
        self.render_puzzle()
        self.setLayout(self.parentLayout)

        #button Connection
        self.picross_puzzle_form.picross_row_table.clicked.connect(self.picross_row_table_clicked_function)
        self.picross_puzzle_form.picross_column_table.clicked.connect(self.picross_column_table_clicked_function)
        self.picross_controller_form.textfile_browse_button.clicked.connect(self.textfile_browse_button_function)
        self.picross_controller_form.puzzle_size_confirm_button.clicked.connect(self.puzzle_size_confirm_function)
        self.picross_controller_form.solve_button.clicked.connect(self.solve_puzzle_function)
        self.picross_controller_form.extract_button.clicked.connect(self.bitmap_extract_function)

        
        #print(self.puzzleValueData)


    def render_puzzle(self):
        self.puzzleMaxRowLength = max([len(x) for x in self.puzzleRowData])
        self.puzzleMaxColumnLength = max([len(x) for x in self.puzzleColumnData])
        
        #Draw Table
        self.picross_puzzle_form.picross_column_table.setModel(picrossColLineModel(self.puzzleColumnData))
        self.picross_puzzle_form.picross_row_table.setModel(picrossRowLineModel(self.puzzleRowData))
        self.picross_puzzle_form.picross_table.setModel(picrossBlockModel(self.puzzleValueData))

        #Resize TableView to fitting size of block
        #-모든 퍼즐 격자가 같은 크기의 정사각형이 되도록 비율(stretch)을 조절한다.
        self.picross_puzzle_form.picross_form.setStretch(0, self.puzzleMaxColumnLength)
        self.picross_puzzle_form.picross_form.setStretch(1, self.puzzleRowSize)

        self.picross_puzzle_form.picross_nhlayout.setStretch(0, self.puzzleMaxRowLength)
        self.picross_puzzle_form.picross_nhlayout.setStretch(1, self.puzzleColumnSize)
        
        self.picross_puzzle_form.picross_shlayout.setStretch(0, self.puzzleMaxRowLength)
        self.picross_puzzle_form.picross_shlayout.setStretch(1, self.puzzleColumnSize)

        #Resize font of block
        fontSize = int(self.height() / (self.puzzleColumnSize + self.puzzleMaxRowLength) * 0.5 - 3) #== 격자 세로 길이의 50% - 3
        self.picross_puzzle_form.picross_column_table.setFont(QtGui.QFont('Arial', fontSize))
        self.picross_puzzle_form.picross_row_table.setFont(QtGui.QFont('Arial', fontSize))
        self.picross_puzzle_form.picross_table.setFont(QtGui.QFont('Arial', fontSize))

        return


    #창 크기 조절될때 발생하는 이벤트 함수
    def resizeEvent(self, event):
        self.resize(event.size())

        # set puzzle.ui's width to make sure puzzle's grid is always square 
        # WHENEVER resized 
        puzzleWidth = int(Decimal(self.puzzleRowSize + self.puzzleMaxRowLength) / Decimal(self.puzzleColumnSize + self.puzzleMaxColumnLength) * self.height())

        self.parentLayout.setStretch(0, puzzleWidth) #=SQUARE
        self.parentLayout.setStretch(1, self.width() - puzzleWidth)
        self.setMinimumWidth(puzzleWidth + 200)

        self.render_puzzle()
        self.update()
    
    def picross_row_table_clicked_function(self):
        clickedRowIndex = self.picross_puzzle_form.picross_row_table.selectedIndexes()[0].row()
        self.picross_line_data_dialog_form.line_info_label.setText("Row " + str(clickedRowIndex + 1) + ":")
        self.picross_line_data_dialog_form.line_data_edit.setText(" ".join(str(x) for x in self.puzzleRowData[clickedRowIndex]))

        dialogResult = self.picross_line_data_dialog_form.exec_()

        if dialogResult: #If User Pressed accepted
            try:
                inputText = self.picross_line_data_dialog_form.line_data_edit.text().replace(",", " ")
                #make also accept int string splited by comma
                int_list_convert = [int(x) for x in inputText.split()]
                
                if len(int_list_convert) + sum(int_list_convert) > self.puzzleRowSize + 1:
                    raise Exception("Sum of numbers is bigger than column size")

                self.puzzleRowData[clickedRowIndex] = int_list_convert
                self.render_puzzle()

            except Exception as e:
                QMessageBox.warning(self, "Warning", "Invalid Input : " + str(e))
                return
        return
    

    def picross_column_table_clicked_function(self):
        clickedColumnIndex = self.picross_puzzle_form.picross_column_table.selectedIndexes()[0].column()
        self.picross_line_data_dialog_form.line_info_label.setText("Column " + str(clickedColumnIndex + 1) + ":")
        self.picross_line_data_dialog_form.line_data_edit.setText(" ".join(str(x) for x in self.puzzleColumnData[clickedColumnIndex]))
        
        dialogResult = self.picross_line_data_dialog_form.exec_()

        if dialogResult: #If User Pressed accepted
            try:
                inputText = self.picross_line_data_dialog_form.line_data_edit.text().replace(",", " ")
                #make also accept int string splited by comma
                int_list_convert = [int(x) for x in inputText.split()]
                
                if len(int_list_convert) + sum(int_list_convert) > self.puzzleColumnSize + 1:
                    raise Exception("Sum of numbers is bigger than column size")

                self.puzzleColumnData[clickedColumnIndex] = int_list_convert
                self.render_puzzle()

            except Exception as e:
                QMessageBox.warning(self, "Warning", "Invalid Input : " + str(e))
                return
        return

    def textfile_browse_button_function(self):
        file_name = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt)")
        self.picross_controller_form.textfile_path.setText(file_name[0])

        try:
            with open(file_name[0], "r") as f:

                
                textFileExtraction = f.readlines()

                #line 1 : puzzle Size Info
                puzzleSizeInfo = [int(x) for x in textFileExtraction[0].replace('\n', '').split()]
                self.puzzleRowSize = puzzleSizeInfo[0]
                self.puzzleColumnSize = puzzleSizeInfo[1]

                if self.puzzleRowSize > 50 or self.puzzleColumnSize > 50:
                    raise Exception("Puzzle size is too large")

                self.puzzleValueData = [[0] * self.puzzleColumnSize for _ in range(self.puzzleRowSize)]

                #line 2 ~ row+1  : puzzle row Info
                self.puzzleRowData = [[int(x) for x in line.replace('\n', '').split()] for line in textFileExtraction[1:self.puzzleRowSize+1]]

                #line row+2 ~ row+column+1 : puzzle column Info
                self.puzzleColumnData = [[int(x) for x in line.replace('\n', '').split()] for line in textFileExtraction[self.puzzleRowSize+1:self.puzzleRowSize+self.puzzleColumnSize+1]]
                

                self.render_puzzle()
        except Exception as e:
            QMessageBox.warning(self, "Warning", "Invalid Input : " + str(e))
            return




    def puzzle_size_confirm_function(self):
        receivedRow = self.picross_controller_form.puzzle_height.value()
        receivedColumn = self.picross_controller_form.puzzle_width.value()
        if type(receivedRow) != int or type(receivedColumn) != int or receivedRow <= 2 or receivedColumn <= 2:
            QMessageBox.warning(self, "Error", "Please enter integer value more than 3")
            return
        
        if receivedRow > 50 or receivedColumn > 50:
            QMessageBox.warning(self, "Error", "Puzzle size is too large")
            return
        
        self.puzzleValueData = [[0 for i in range(receivedColumn)] for j in range(receivedRow)]
        self.puzzleRowData = [[0] * (receivedRow // 4 + 1) for i in range(receivedRow)]
        self.puzzleColumnData = [[0] * (receivedColumn // 4 + 1) for i in range(receivedColumn)]
        self.puzzleRowSize = receivedRow
        self.puzzleColumnSize = receivedColumn
        self.render_puzzle()


    def bitmap_extract_function(self):
        blockPixel = int(16)
        colortableSize = int(8)
        headerSize = int(54)
        pixelAreaSize = (blockPixel ** 2 * self.puzzleRowSize * self.puzzleColumnSize) // 8 + int(((blockPixel ** 2 * self.puzzleRowSize * self.puzzleColumnSize) != 0))
        BMPfileSize = headerSize + colortableSize + pixelAreaSize

        def write_itos_biglittle(writeStream, num, byteSize):
            for i in range(byteSize):
                writeStream.write(bytes([int(num) & 0xFF]))
                num >>= 8

        name = QFileDialog.getSaveFileName(self, 'Save File', '', 'BMP Files (*.bmp)')
        file = open(name[0] + '', 'wb')

        #https://docs.fileformat.com/image/bmp/  (BMP file format 설명 참고 링크)
        
        # [1] BitmapFileHeader (14 bytes)
        file.write(bytes('BM', 'utf-8'))
        #2 byte : Identify File format which is Bitmap (2/14 bytes)
        write_itos_biglittle(file, BMPfileSize, 4)
        #4 byte : BMPfileSize (6/14 bytes)
        file.write(bytes('\x00\x00\x00\x00', 'utf-8'))
        #4 byte : Reserved (10/14 bytes)
        write_itos_biglittle(file, headerSize + colortableSize, 4)
        #4 byte : Offset to start of pixel data (14/14 bytes)


        # [2] DIB Header : BITMAPINFOHEADER (40 bytes)

        write_itos_biglittle(file, 40, 4)
        #4 byte : DIB Header Size (4/40 bytes)
        write_itos_biglittle(file, blockPixel * self.puzzleRowSize, 4)
        #4 byte : Image Width (8/40 bytes)
        write_itos_biglittle(file, blockPixel * self.puzzleColumnSize, 4)
        #4 byte : Image Height (12/40 bytes)
        write_itos_biglittle(file, 1, 2)
        #2 byte : Number of color planes (14/40 bytes)
        write_itos_biglittle(file, 1, 2)
        #2 byte : Number of bits per pixel == 1(just White or Black) (16/40 bytes)
        write_itos_biglittle(file, 0, 4)
        #4 byte : Compression Method (value 0 is no compression) (20/40 bytes)
        write_itos_biglittle(file, BMPfileSize - 56, 4)
        #4 byte : Image Size (24/40 bytes)
        write_itos_biglittle(file, 3200, 4)
        #4 byte : Horizontal Resolution of pixel per meter (28/40 bytes)
        write_itos_biglittle(file, 3200, 4)
        #4 byte : Vertical Resolution of pixel per meter (32/40 bytes)
        write_itos_biglittle(file, 0, 4)
        #4 byte : Number of colors in the palette - generally 0 (36/40 bytes)
        write_itos_biglittle(file, 0, 4)
        #4 byte : Number of important colors used - generally 0 (40/40 bytes)

        # [3] Color Table : color table (this picture's bits per pixel is 1 and color table is necessary when bits per pixel <= 8) (8 bytes)
        write_itos_biglittle(file, 0xFFFFFF, 4)
        # bit 0 means white color (0xFFFFFF)
        write_itos_biglittle(file, 0, 4); 
        # bit 1 means black color (0x000000)

        # [4] Pixel Data
        #bitmap data is stored in the order of the rows from the bottom to the top of the bitmap.
        #so, we need to reverse the order of the rows.
        for rowData in reversed(self.puzzleValueData):
            rowBinaryString = ''
            for blockData in rowData:
                if blockData == 2: #YES
                    rowBinaryString += '1' * blockPixel
                else:
                    rowBinaryString += '0' * blockPixel
            
            index = 0
            buffer = bytearray()
            while index < len(rowBinaryString):
                buffer.append(int(rowBinaryString[index:index+8], 2))
                index += 8
            
            for i in range(blockPixel):
                file.write(buffer)

        file.close()




    class PicrossSolvingThread(QThread):
        class PicrossProgressingThread(QThread):

            progressMade = QtCore.pyqtSignal(int)

            def __init__(self, AbstractPicross):
                super().__init__()
                self.AbstractPicross = AbstractPicross
            
            def run(self):
                currentProgress = 0
                while True:
                    if currentProgress != self.AbstractPicross.progress:
                        currentProgress = self.AbstractPicross.progress
                        self.progressMade.emit(currentProgress)


        progressMade = QtCore.pyqtSignal(int)

        def __init__(self, AbstractPicross):
            QThread.__init__(self)
            self.AbstractPicross = AbstractPicross

        def run(self):
            self.progressingThread = self.PicrossProgressingThread(self.AbstractPicross)
            self.progressingThread.progressMade.connect(self.progressUpdate)
            self.progressingThread.start()
            self.AbstractPicross.solve()
            self.progressingThread.terminate()

        def progressUpdate(self, progress_done):
            self.progressMade.emit(progress_done)

        def terminate(self):
            self.progressingThread.terminate()
            QThread.terminate(self)
    
    



            
    

    def solve_puzzle_function(self):
        self.testBoard = AbstractPicrossBoardClass(self.puzzleRowSize, self.puzzleColumnSize, self.puzzleRowData, self.puzzleColumnData)
        
        self.solvingThread = self.PicrossSolvingThread(self.testBoard)
        self.waiting = True
    
        progressMax = self.testBoard.progressUnit
        self.puzzle_solving_progress = QProgressDialog("Puzzle size more than 30x30 may take MUCH time to solve", "Cancel", 0, progressMax, self)
        self.puzzle_solving_progress.setMinimumDuration(1000)
        self.puzzle_solving_progress.setWindowTitle("Solving Progress")
        self.puzzle_solving_progress.setWindowModality(Qt.WindowModal)
        self.puzzle_solving_progress.canceled.connect(self.solve_cancel)
        self.puzzle_solving_progress.closeEvent = self.solve_cancel
        self.puzzle_solving_progress.show()
        self.solvingThread.progressMade.connect(self.puzzle_solving_progress.setValue)
        self.solvingThread.start()
        while self.testBoard.progress < progressMax - 10 and self.waiting is True:
            self.puzzle_solving_progress.setValue(self.testBoard.progress)
        
        if self.waiting is True:
            print("Success process")
            self.solvingThread.wait()
            self.puzzleValueData = self.testBoard.board
            self.puzzle_solving_progress.close()
        else:
            print("terminated process")
            
        self.render_puzzle()

    def solve_cancel(self, event=None):
        self.waiting = False
        self.solvingThread.terminate()
        




if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스
    initWindow = Window()

    #탐색 창 숨기기
    #myWindow.setWindowFlag(Qt.FramelessWindowHint)
    #프로그램 화면을 보여주는 코드
    initWindow.show()

    #프로그램을 이벤트 루프로 진입시키는(프로그램 작동) 코드
    sys.exit(app.exec_())



'''
############################################### absolete following ######################################

class picrossPuzzleWindow:
    def __init__(self, puzzleTextList=list(), puzzleGridTable=list()):
        self.x_size = puzzleTextList[0][1]
        self.y_size = puzzleTextList[0][0]
        self.fontSize = 4
        self.blockMinSize = 10
        self.maxRowLength = max([len(x) for x in puzzleTextList[1:1+self.y_size]])
        self.maxColLength = max([len(x) for x in puzzleTextList[1+self.y_size:]])

        self.picrossColWindow = QTableView()
        self.picrossColWindow.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.picrossColWindow.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.picrossColWindow.setModel(picrossColLineModel(puzzleTextList[1+self.y_size:]))
        self.picrossColWindow.setFont(QtGui.QFont('Arial', self.fontSize))
        self.picrossColWindow.verticalScrollBar().setDisabled(True)
        self.picrossColWindow.horizontalScrollBar().setDisabled(True)
        self.picrossColWindow.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.picrossColWindow.horizontalHeader().setMinimumSectionSize(self.blockMinSize)
        self.picrossColWindow.horizontalHeader().setDefaultSectionSize(self.blockMinSize)
        self.picrossColWindow.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.picrossColWindow.verticalHeader().setMinimumSectionSize(self.blockMinSize)
        self.picrossColWindow.verticalHeader().setDefaultSectionSize(self.blockMinSize)
        self.picrossColWindow.horizontalHeader().hide()
        self.picrossColWindow.verticalHeader().hide()

        
        self.picrossRowWindow = QTableView()
        self.picrossRowWindow.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.picrossRowWindow.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.picrossRowWindow.setModel(picrossRowLineModel(puzzleTextList[1:1+self.y_size]))
        self.picrossRowWindow.setFont(QtGui.QFont('Arial', self.fontSize))
        self.picrossRowWindow.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.picrossRowWindow.horizontalHeader().setMinimumSectionSize(self.blockMinSize)
        self.picrossRowWindow.horizontalHeader().setDefaultSectionSize(self.blockMinSize)
        self.picrossRowWindow.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.picrossRowWindow.verticalHeader().setMinimumSectionSize(self.blockMinSize)
        self.picrossRowWindow.verticalHeader().setDefaultSectionSize(self.blockMinSize)
        self.picrossRowWindow.horizontalHeader().hide()
        self.picrossRowWindow.verticalHeader().hide()

        self.picrossTable = QTableView()
        self.picrossTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.picrossTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.picrossTable.setModel(picrossBlockModel(puzzleGridTable))
        self.picrossTable.setFont(QtGui.QFont('Arial', self.fontSize))
        self.picrossTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  #wrap_content 같은 느낌 
        self.picrossTable.horizontalHeader().setMinimumSectionSize(self.blockMinSize)
        self.picrossTable.horizontalHeader().setDefaultSectionSize(self.blockMinSize)
        self.picrossTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.picrossTable.verticalHeader().setMinimumSectionSize(self.blockMinSize)
        self.picrossTable.verticalHeader().setDefaultSectionSize(self.blockMinSize)
        self.picrossTable.horizontalHeader().hide()
        self.picrossTable.verticalHeader().hide()

        #Upper side Sub
        self.upperLayout = QHBoxLayout()
        self.upperLayout.addWidget(QLabel("Puzzle"), self.maxRowLength)
        self.upperLayout.addWidget(self.picrossColWindow, self.x_size)

        #Lower side Sub
        self.lowerLayout = QHBoxLayout()
        self.lowerLayout.addWidget(self.picrossRowWindow, self.maxRowLength)
        self.lowerLayout.addWidget(self.picrossTable, self.x_size)

        #Main Layout
        self.puzzleLayout = QVBoxLayout()
        self.puzzleLayout.setSpacing(0)
        self.puzzleLayout.addLayout(self.upperLayout, self.maxColLength)
        self.puzzleLayout.addLayout(self.lowerLayout, self.y_size)

    def layout(self):
        return self.puzzleLayout
        
'''