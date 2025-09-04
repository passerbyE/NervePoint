import sys
import json
import os
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QApplication,  QDockWidget, QListWidget, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem
# 匯入 QAction 以建立選單項目
from PyQt6.QtGui import QColor, QBrush, QPen, QPainter, QAction
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
        
        # 參數
        self.lastDockChange = True # 初始化 lastDockChange 屬性
        
        self.setWindowTitle("NervePoint")
        self.setGeometry(560, 240, 800, 600)
        
        # --- 全域高對比樣式設定 ---
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E; /* 深灰色背景 */
                color: #D4D4D4;           /* 淺灰色文字 */
            }
            QMenuBar {
                background-color: #2D2D2D;
                color: #D4D4D4;
            }
            QMenuBar::item:selected {
                background-color: #3E3E3E;
                color: #D4D4D4;
            }
            QMenu {
                background-color: #252526;
                border: 1px solid #3E3E3E;
                color: #D4D4D4;
            }
            QMenu::item:selected{
                background-color: #3E3E3E;
                color: #D4D4D4;
            }
            QListWidget::item:selected {
                background-color: #4b4b4b;
                color: #D4D4D4;
            }
            QDockWidget::title {
                background-color: #353535;
                color: #D4D4D4; 
                text-align: Left;
                padding: 4px;
            }
        """)

        # --- 建立選單列 ---
        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("檢視(&V)")
        # 建立一個動作來顯示/重置側邊欄
        reset_dock_action = QAction("顯示 Do List", self)
        reset_dock_action.triggered.connect(self.reset_todo_dock)
        view_menu.addAction(reset_dock_action)
        
        # --- 側邊欄dolist（可停靠部件 QDockWidget） ---
        self.todo_dock = QDockWidget("Nerve Do List", self)
        self.todo_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        
        
        # --- 將 QDockWidget 和 QListWidget 的樣式合併並設定在 Dock 上 ---
        self.todo_dock.setStyleSheet("""
            QDockWidget {
                /* 雖然 QMainWindow 已設定，但這裡可以再次確保 */
                color: #D4D4D4; 
            }
            QDockWidget::title {
                background-color: #353535;
                color: #D4D4D4; /* 明確設定標題文字顏色 */
                text-align: Left;
                padding: 4px;
            }
            QListWidget {
                background-color: #252525;
                color: #D4D4D4;
                border: none;
                font-size: 14px;
            }
            QListWidget::item:hover {
                background-color: #3b3b3b;
            }
            QListWidget::item:selected {
                background-color: #4b4b4b;
                color: white;
            }
        """)


        todo_container = QWidget()
        todo_layout = QVBoxLayout()
        self.todo_list = QListWidget()
        # --- QListWidget 的高對比樣式 (樣式已移至上方) ---
        
        self.todo_list.addItem("代辦1: 完成節點設計")
        self.todo_list.addItem("代辦2: 實現連線功能")
        self.todo_list.addItem("代辦3: 儲存與讀取")
        todo_layout.addWidget(self.todo_list)
        todo_container.setLayout(todo_layout)
        self.todo_dock.setWidget(todo_container)
        
        #初始並創建todo 的 dock 到左側
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.todo_dock)
        
        # 連接 visibilityChanged 信號
        self.todo_dock.visibilityChanged.connect(self.todo_dock_visibilityChange)
        
        # 這裡是所有圖形項目的容器
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QColor("#181818"))
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
        self.builtRect(0, 0)

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
        # 這個矩形的背景是淺灰色 (#DBDBDB)
        rect_item.setBrush(QBrush(QColor("#DBDBDB"))) 
        rect_item.setPen(QPen(QColor("#C4C4C4"), 2))
        self.scene.addItem(rect_item)

        # --- 在淺色矩形上新增深色文字 ---
        # 為了形成對比，我們在淺色背景上使用黑色文字
        text_on_rect = QGraphicsTextItem("節點文字", parent=rect_item)
        text_on_rect.setDefaultTextColor(QColor("#000000")) # 設定文字為黑色
        # 稍微調整文字位置使其在矩形內居中
        text_on_rect.setPos(posX + 15, posY + 12)
        self.scene.addItem(text_on_rect)

        
    # QDockWidget 的 visibilityChanged 信號會傳遞一個布林值 (visible)
    def todo_dock_visibilityChange(self, visible):
        if(visible != self.lastDockChange and visible == False):
            print("do list 被關閉")
        self.lastDockChange = visible

    # --- 新增遺失的方法 ---
    def reset_todo_dock(self):
        """
        此方法會將 Do List 側邊欄顯示在左側。
        """
        print("執行復位側邊欄...")
        # 1. 將 QDockWidget 重新加入到主視窗的左側停靠區
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.todo_dock)
        # 2. 確保它是可見的
        self.todo_dock.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NervePoint()
    window.show()
    sys.exit(app.exec())
