from PyQt6.QtWidgets import *
import sys

class NervePoint(QMainWindow):
    def __init__(self):
        super(NervePoint, self).__init__()
        self.setGeometry(500, 200 ,1000, 600)
        self.setWindowTitle("NervePoint")
        
        self.initUI()
        
    def initUI(self):
        self.lable = QLabel(self)
        self.lable.setText("hello world")
        self.lable.move(10, 30)

        self.button = QPushButton(self)
        self.button.setText("this is a button")
        self.button.move(100, 10)
        self.button.clicked.connect(self.clicked)

    def clicked(self):
        self.lable.setText("you click the button")
        self.update()
        
    def update(self):
        self.lable.adjustSize()
    
    



def window():
    app = QApplication(sys.argv)
    win = NervePoint()
    win.show()
    sys.exit(app.exec())
    
window()
