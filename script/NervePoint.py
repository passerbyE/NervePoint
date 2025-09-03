import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt6.QtGui import QColor, QBrush, QPen, QPainter
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets


script_dir = os.path.dirname(os.path.abspath(__file__))
# 往上一層，取得專案的根目錄 (d:\NervePoint)
project_root = os.path.dirname(script_dir)
# 組合出 JSON 檔案的絕對路徑
json_path = os.path.join(project_root, '.json', 'node.json')


with open(json_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)
    
for i in json_data["nodeList"]:
    print(f"節點{i['id']}: \t 文字={i['Text']}\t 父節點={i['FatherNodeid']}\t 座標={i['coordinate']}")


class NervePoint(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NervePoint")
        self.setGeometry(0, 0, 800, 600)
        self.setStyleSheet("background-color: #000000;")
        
        # 這裡是所有圖形項目的容器
        self.scene = QGraphicsScene()
        # 設定場景的背景顏色
        self.scene.setBackgroundBrush(QColor("#181818"))
        # 您也可以設定場景的範圍，例如 (-200, -200) 到 (200, 200)
        self.scene.setSceneRect(0, 0, 1000, 1000)

        # 2. 建立一些 QGraphicsItem (圖形項目) 並加入場景
        
        # 建立一個矩形
        # QGraphicsRectItem(x, y, width, height)
        rect_item = QGraphicsRectItem(10, 10, 100, 50)
        rect_item.setBrush(QBrush(QColor("#DBDBDB"))) # 設定填充顏色
        rect_item.setPen(QPen(QColor("#C4C4C4"), 2))   # 設定邊框樣式
        self.scene.addItem(rect_item)


        # 建立一個文字項目
        text_item = QGraphicsTextItem("Hello, QGraphicsScene!")
        text_item.setPos(0, -50) # 設定文字位置
        text_item.setDefaultTextColor(QColor("purple"))
        font = text_item.font()
        font.setPointSize(16)
        text_item.setFont(font)
        self.scene.addItem(text_item)

        # 3. 建立一個 QGraphicsView (檢視/視窗)
        # 這是用來 "觀看" 場景的 widget
        self.view = QGraphicsView(self.scene, self)
        self.view.horizontalScrollBar().setValue(1)
        self.view.verticalScrollBar().setValue(1)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing) # 反鋸齒

        # --- 自訂捲動軸樣式 ---
        # 使用 QSS (Qt Style Sheets) 來美化捲動軸
        # 這段程式碼會將捲動軸改成現代化的簡潔風格
        stylesheet = """
            QScrollBar:vertical {
                border: none;
                background: #181818;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #606060;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #808080;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

            QScrollBar:horizontal {
                border: none;
                background: #181818;
                height: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background: #606060;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #808080;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """
        self.view.setStyleSheet(stylesheet)
        # --- 樣式設定結束 ---

        # 4. 將 QGraphicsView 設置為中央 widget
        self.setCentralWidget(self.view)



        #工作區

        # 雙擊事件
        def on_double_click(event):
            print("Mouse double clicked at:", event.pos())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NervePoint()
    window.show()
    sys.exit(app.exec())
