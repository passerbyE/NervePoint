import sys
import json
import os
import keyboard as kb
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QApplication,  QDockWidget, QListWidget, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem
# 匯入 QAction 以建立選單項目
from PyQt6.QtGui import QColor, QBrush, QPen, QPainter, QAction, QTextCursor
from PyQt6.QtCore import Qt


# --- 組合路徑的程式碼 ... ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
json_path = os.path.join(project_root, '.json', 'node.json')


# --- 自訂圖形項目類別 ---

class NodeTextItem(QGraphicsTextItem):
    """自訂的文字項目，處理編輯邏輯"""
    def focusOutEvent(self, event):
        # 當文字失去焦點時 (編輯完成)，設回不可編輯狀態
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        #取消反白
        curser = self.textCursor()
        curser.clearSelection()
        self.setTextCursor(curser)
        
        super().focusOutEvent(event)
        # 在這裡可以加入更新 JSON 資料的邏輯

class NodeRectItem(QGraphicsRectItem):
    """自訂的方塊項目，處理雙擊事件"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_item = None # 用來存放對應的文字項目

    def set_text_item(self, text_item):
        self.text_item = text_item

    def mouseDoubleClickEvent(self, event):
        # 當方塊被雙擊時，讓其內部的文字進入編輯模式
        if self.text_item:
            self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.text_item.setFocus()
            # 選取所有文字
            cursor = self.text_item.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            self.text_item.setTextCursor(cursor)
        # 呼叫父類別的方法，以防有其他預設行為
        super().mouseDoubleClickEvent(event)


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

        # --- 創建todo 物件 ---
        todo_container = QWidget()
        todo_layout = QVBoxLayout()
        self.todo_list = QListWidget()
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
        # --- #1：將雙擊事件綁定到 Scene ---
        self.scene.mouseDoubleClickEvent = self.on_scene_double_click
        self.scene.setBackgroundBrush(QColor("#181818"))

        # 3. 建立一個 QGraphicsView (檢視/視窗)
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing) # 反鋸齒
        
        # --- 修正 #2：移除對 View 事件的覆寫 ---
        # self.view.mouseDoubleClickEvent = self.on_double_click # <--- 刪除或註解掉這行
        
        

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
    
    
    # --- 將巢狀函式移到此處，並轉換為類別方法 ---

    # --- 修正 #3：重新命名並修改此方法以處理 Scene 事件 ---
    def on_scene_double_click(self, event):
        # 檢查點擊位置下方是否有圖形項目
        # event.scenePos() 直接提供場景座標
        scene_pos = event.scenePos()
        item = self.scene.itemAt(scene_pos, self.view.transform())
        
        # 如果 item 是 None，表示點擊在空白處
        if item is None:
            print("在空白處雙擊，建立新方塊...")
            self.builtRect(scene_pos.x(), scene_pos.y())
        else:
            # 如果點擊在現有項目上，則呼叫 QGraphicsScene 的預設處理方式
            # 這樣事件才能被正確傳遞給被點擊的項目 (NodeRectItem)
            print("在現有項目上雙擊")
            QGraphicsScene.mouseDoubleClickEvent(self.scene, event)


    # 設置分塊
    def builtRect(self, posX, posY):
        # --- 使用自訂的 NodeRectItem ---
        rect_item = NodeRectItem(posX - 50, posY - 25, 100, 50)
        
        rect_item.setBrush(QBrush(QColor("#DBDBDB"))) 
        rect_item.setPen(QPen(QColor("#C4C4C4"), 2))
        rect_item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.scene.addItem(rect_item)

        # --- 使用自訂的 NodeTextItem ---
        text_on_rect = NodeTextItem("now node", parent=rect_item)
        text_on_rect.setDefaultTextColor(QColor("#000000"))
        
        # 讓方塊知道它的文字項目是誰
        rect_item.set_text_item(text_on_rect)
        
        # --- 文字置中邏輯 (保持不變) ---
        rect_width = rect_item.rect().width()
        rect_height = rect_item.rect().height()
        text_width = text_on_rect.boundingRect().width()
        text_height = text_on_rect.boundingRect().height()
        center_x = (rect_width - text_width) / 2
        center_y = (rect_height - text_height) / 2
        text_on_rect.setPos((posX - 50) + center_x,(posY - 25) + center_y)

        # --- 讓新建的文字立即進入編輯模式 (保持不變) ---
        text_on_rect.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        text_on_rect.setFocus()
        cursor = text_on_rect.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        text_on_rect.setTextCursor(cursor)

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

    # --- 資料新增 ---
    # def renew_data(self, id, Text, FatherNodeid, coordinate):
    # {
    #     try:
    #         with open(json_path, 'w', encoding='utf-8') as f:
    #             json.dump(self.json_data, f, ensure_ascii=False, indent=4)
    #             f
    # }

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NervePoint()
    window.show()
    sys.exit(app.exec())
