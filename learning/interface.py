import sys
import json
import os
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QApplication,  QDockWidget, QListWidget, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt6.QtGui import QColor, QBrush, QPen, QPainter
from PyQt6.QtCore import Qt



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
        self.setGeometry(560, 240, 800, 600)
        self.setStyleSheet("background-color: #000000;")
        
        # --- 側邊欄dolist（可停靠部件 QDockWidget） ---
        self.todo_dock = QDockWidget("待辦清單", self)
        self.todo_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        todo_container = QWidget()
        todo_layout = QVBoxLayout()
        self.todo_list = QListWidget()
        self.todo_list.addItem("代辦1: ")
        self.todo_list.addItem("代辦2: ")
        self.todo_list.addItem("代辦3: ")
        todo_layout.addWidget(self.todo_list)
        todo_container.setLayout(todo_layout)
        self.todo_dock.setWidget(todo_container)
        
        #初始並創建todo 的 dock 到左側
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.todo_dock)
        
        # 修正：連接到類別的方法 self.todo_dock_visibilityChange
        self.todo_dock.visibilityChanged.connect(self.todo_dock_visibilityChange)
        
        # 這裡是所有圖形項目的容器
        self.scene = QGraphicsScene()
        # 設定場景的背景顏色
        self.scene.setBackgroundBrush(QColor("#181818"))
        # 設定場景的範圍
        self.scene.setSceneRect(0, 0, 200, 200)

        # 3. 建立一個 QGraphicsView (檢視/視窗)
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing) # 反鋸齒
        
        

        # --- 自訂捲動軸樣式 ---
        # 使用 QSS (Qt Style Sheets) 來美化捲動軸
        # 這段程式碼會將捲動軸改成現代化的簡潔風格
        stylesheet = """
            QScrollBar:vertical { border: none; background: #181818; width: 8px; margin: 0px; }
            QScrollBar::handle:vertical { background: #606060; min-height: 20px; border-radius: 6px; }
            QScrollBar::handle:vertical:hover { background: #808080; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
            QScrollBar:horizontal { border: none; background: #181818; height: 8px; margin: 0px; }
            QScrollBar::handle:horizontal { background: #606060; min-width: 20px; border-radius: 6px; }
            QScrollBar::handle:horizontal:hover { background: #808080; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
        """
            
        self.view.setStyleSheet(stylesheet)
        # --- 樣式設定結束 ---

        # 呼叫方法來建立初始的矩形
        self.builtRect(1000, 0)

    # --- 將巢狀函式移到此處，並轉換為類別方法 ---

    # 雙擊事件 (注意：這個事件目前沒有被連接到任何元件上)
    def on_double_click(self, event):
        print("Mouse double clicked at:", event.pos())
    
    # 設置分塊
    def builtRect(self, posX, posY):
        # 建立一個矩形
        # QGraphicsRectItem(x, y, width, height)
        
        #修改畫面大小的地方要改
        #self.veiw.setSceneRect(0, 0, posX + 100, posY + 100)
        
        rect_item = QGraphicsRectItem(posX, posY, 100, 50)
        rect_item.setBrush(QBrush(QColor("#DBDBDB"))) # 設定填充顏色
        rect_item.setPen(QPen(QColor("#C4C4C4"), 2))   # 設定邊框樣式
        self.scene.addItem(rect_item)
        
    # QDockWidget 的 visibilityChanged 信號會傳遞一個布林值 (visible)
    # 所以方法需要能夠接收它
    def todo_dock_visibilityChange(self, visible):
        print(f"待辦清單的可見性已變更為: {visible}")
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NervePoint()
    window.show()
    sys.exit(app.exec())
