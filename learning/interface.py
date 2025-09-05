import sys
import json
import os
# 移除未使用的 keyboard 匯入
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QApplication,  QDockWidget, QListWidget, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt6.QtGui import QColor, QBrush, QPen, QPainter, QAction, QTextCursor
from PyQt6.QtCore import Qt, QTimer
import random as rd

# --- 變數 特殊 設定用---
dataUpdateTime = 5000
summonWorld = ["NODE", "(∠ ω< )⌒☆"]
probabilities = [19, 1]


# --- 組合路徑的程式碼 ... ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
# 修正：您的 JSON 檔案路徑應該是 .json 而不是 .data
json_path = os.path.join(project_root, '.json', 'node.json')


# --- 自訂圖形項目類別 ---

class NodeTextItem(QGraphicsTextItem):
    """自訂的文字項目，處理編輯邏輯並回報變更"""
    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)  
        super().focusOutEvent(event)
        
        # 回報機制：文字已變更
        parent_rect = self.parentItem()
        if parent_rect and hasattr(parent_rect, 'main_window'):
            parent_rect.main_window.update_node_text(parent_rect.node_id, self.toPlainText())

class NodeRectItem(QGraphicsRectItem):
    """自訂的方塊項目，處理雙擊事件並回報變更"""
    def __init__(self, node_id, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node_id = node_id
        self.main_window = main_window
        self.text_item = None

    def set_text_item(self, text_item):
        self.text_item = text_item

    def mouseDoubleClickEvent(self, event):
        if self.text_item:
            self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.text_item.setFocus()
            cursor = self.text_item.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            self.text_item.setTextCursor(cursor)
        super().mouseDoubleClickEvent(event)

    def itemChange(self, change, value):
        # 回報機制：位置已變更
        if change == self.GraphicsItemChange.ItemPositionHasChanged:
            self.main_window.update_node_position(self.node_id, self.pos())
        return super().itemChange(change, value)


class NervePoint(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 讀取節點資料到 self.json_data
        self.json_data = self.load_data()
        
        # 儲存用timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.save_data) # 連接到正確的儲存函式
        self.timer.start(dataUpdateTime)
        print(f"自動儲存已啟用，每 {dataUpdateTime/1000} 秒儲存一次。")
        
        # 參數
        self.lastDockChange = True
        
        self.setWindowTitle("NervePoint")
        self.setGeometry(560, 240, 800, 600)
        
        # 建立所有 UI 元件
        self.setup_ui()
        
        # 根據讀取的資料，在畫布上建立所有節點
        self.load_nodes_from_data()

    def setup_ui(self):
        # (這裡放入您所有建立 menu, dock, scene, view 的程式碼)
        self.setStyleSheet("QMainWindow { background-color: #1E1E1E; ... }") # 樣式表省略
        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("檢視(&V)")
        reset_dock_action = QAction("顯示 Do List", self)
        reset_dock_action.triggered.connect(self.reset_todo_dock)
        view_menu.addAction(reset_dock_action)
        self.todo_dock = QDockWidget("Nerve Do List", self)
        # ... (todo_dock 的設定) ...
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.todo_dock)
        self.scene = QGraphicsScene()
        self.scene.mouseDoubleClickEvent = self.on_scene_double_click
        self.scene.setBackgroundBrush(QColor("#181818"))
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        # ... (捲動軸樣式設定) ...

    # --- 資料處理方法 ---
    def load_data(self):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"成功從 {json_path} 讀取資料。")
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"警告：找不到或無法解析 {json_path}。將使用空資料。")
            return {"nodeList": []}

    def save_data(self):
        """
        【正確的寫入方法】
        使用 'w' 模式和 json.dump() 將記憶體中的資料寫入檔案。
        """
        print(f"執行自動儲存...")
        try:
            # 確保目標資料夾存在
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                # 使用 json.dump() 將 self.json_data 寫入檔案 f
                json.dump(self.json_data, f, ensure_ascii=False, indent=4)
            print("儲存成功。")
        except Exception as e:
            print(f"寫入 node_data 失敗: {e}")

    def closeEvent(self, event):
        """在關閉應用程式前，執行最後一次儲存"""
        print("正在關閉應用程式，執行最後儲存...")
        self.save_data()
        super().closeEvent(event)

    def get_node_by_id(self, node_id):
        for node in self.json_data["nodeList"]:
            if node["id"] == node_id:
                return node
        return None

    def update_node_text(self, node_id, new_text):
        node = self.get_node_by_id(node_id)
        if node:
            node["Text"] = new_text
            print(f"資料更新(文字): ID={node_id}")

    def update_node_position(self, node_id, new_pos):
        node = self.get_node_by_id(node_id)
        if node:
            node["coordinate"] = [new_pos.x(), new_pos.y()]
            print(f"資料更新(位置): ID={node_id}")

    def load_nodes_from_data(self):
        """讀取 self.json_data 並在畫布上建立所有節點"""
        for node_data in self.json_data["nodeList"]:
            self.builtRect(node_data["coordinate"][0], node_data["coordinate"][1], node_data=node_data)

    # --- 事件與物件創建方法 ---
    def on_scene_double_click(self, event):
        scene_pos = event.scenePos()
        item = self.scene.itemAt(scene_pos, self.view.transform())
        
        if item is None:
            print("在空白處雙擊，建立新方塊...")
            # 1. 決定新節點的 ID
            new_node_id = (max([n["id"] for n in self.json_data["nodeList"]]) if self.json_data["nodeList"] else 0) + 1
            
            # 2. 建立新節點的資料字典
            new_node_data = {
                "id": new_node_id,
                "Text": rd.choices(summonWorld, weights=probabilities, k=1)[0],
                "FatherNodeid": None,
                "coordinate": [scene_pos.x(), scene_pos.y()]
            }
            
            # 3. 將新資料加入到記憶體中的 self.json_data
            self.json_data["nodeList"].append(new_node_data)
            print(f"資料新增(創建): {new_node_data}")
            
            # 4. 呼叫 builtRect 在畫布上建立視覺物件
            self.builtRect(scene_pos.x(), scene_pos.y(), node_data=new_node_data, edit_on_create=True)
        else:
            QGraphicsScene.mouseDoubleClickEvent(self.scene, event)

    def builtRect(self, posX, posY, node_data, edit_on_create=False):
        # 傳入 ID 和主視窗引用
        rect_item = NodeRectItem(node_data["id"], self, posX - 50, posY - 25, 100, 50)
        
        rect_item.setBrush(QBrush(QColor("#DBDBDB"))) 
        rect_item.setPen(QPen(QColor("#C4C4C4"), 2))
        rect_item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        rect_item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.scene.addItem(rect_item)

        text_on_rect = NodeTextItem(node_data["Text"], parent=rect_item)
        text_on_rect.setDefaultTextColor(QColor("#000000"))
        rect_item.set_text_item(text_on_rect)
        
        # 文字置中
        rect_width = rect_item.rect().width()
        rect_height = rect_item.rect().height()
        text_width = text_on_rect.boundingRect().width()
        text_height = text_on_rect.boundingRect().height()
        center_x = (rect_width - text_width) / 2
        center_y = (rect_height - text_height) / 2
        text_on_rect.setPos(center_x, center_y)

        if edit_on_create:
            text_on_rect.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            text_on_rect.setFocus()
            cursor = text_on_rect.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            text_on_rect.setTextCursor(cursor)

    def reset_todo_dock(self):
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.todo_dock)
        self.todo_dock.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NervePoint()
    window.show()
    sys.exit(app.exec())
import sys
import json
import os
# 移除未使用的 keyboard 匯入
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QApplication,  QDockWidget, QListWidget, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt6.QtGui import QColor, QBrush, QPen, QPainter, QAction, QTextCursor
from PyQt6.QtCore import Qt, QTimer
import random as rd

# --- 變數 特殊 設定用---
dataUpdateTime = 5000
summonWorld = ["NODE", "(∠ ω< )⌒☆"]
probabilities = [19, 1]


# --- 組合路徑的程式碼 ... ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
# 修正：您的 JSON 檔案路徑應該是 .json 而不是 .data
json_path = os.path.join(project_root, '.json', 'node.json')


# --- 自訂圖形項目類別 ---

class NodeTextItem(QGraphicsTextItem):
    """自訂的文字項目，處理編輯邏輯並回報變更"""
    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)  
        super().focusOutEvent(event)
        
        # 回報機制：文字已變更
        parent_rect = self.parentItem()
        if parent_rect and hasattr(parent_rect, 'main_window'):
            parent_rect.main_window.update_node_text(parent_rect.node_id, self.toPlainText())

class NodeRectItem(QGraphicsRectItem):
    """自訂的方塊項目，處理雙擊事件並回報變更"""
    def __init__(self, node_id, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node_id = node_id
        self.main_window = main_window
        self.text_item = None

    def set_text_item(self, text_item):
        self.text_item = text_item

    def mouseDoubleClickEvent(self, event):
        if self.text_item:
            self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.text_item.setFocus()
            cursor = self.text_item.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            self.text_item.setTextCursor(cursor)
        super().mouseDoubleClickEvent(event)

    def itemChange(self, change, value):
        # 回報機制：位置已變更
        if change == self.GraphicsItemChange.ItemPositionHasChanged:
            self.main_window.update_node_position(self.node_id, self.pos())
        return super().itemChange(change, value)


class NervePoint(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 讀取節點資料到 self.json_data
        self.json_data = self.load_data()
        
        # 儲存用timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.save_data) # 連接到正確的儲存函式
        self.timer.start(dataUpdateTime)
        print(f"自動儲存已啟用，每 {dataUpdateTime/1000} 秒儲存一次。")
        
        # 參數
        self.lastDockChange = True
        
        self.setWindowTitle("NervePoint")
        self.setGeometry(560, 240, 800, 600)
        
        # 建立所有 UI 元件
        self.setup_ui()
        
        # 根據讀取的資料，在畫布上建立所有節點
        self.load_nodes_from_data()

    def setup_ui(self):
        # (這裡放入您所有建立 menu, dock, scene, view 的程式碼)
        self.setStyleSheet("QMainWindow { background-color: #1E1E1E; ... }") # 樣式表省略
        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("檢視(&V)")
        reset_dock_action = QAction("顯示 Do List", self)
        reset_dock_action.triggered.connect(self.reset_todo_dock)
        view_menu.addAction(reset_dock_action)
        self.todo_dock = QDockWidget("Nerve Do List", self)
        # ... (todo_dock 的設定) ...
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.todo_dock)
        self.scene = QGraphicsScene()
        self.scene.mouseDoubleClickEvent = self.on_scene_double_click
        self.scene.setBackgroundBrush(QColor("#181818"))
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        # ... (捲動軸樣式設定) ...

    # --- 資料處理方法 ---
    def load_data(self):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"成功從 {json_path} 讀取資料。")
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"警告：找不到或無法解析 {json_path}。將使用空資料。")
            return {"nodeList": []}

    def save_data(self):
        """
        【正確的寫入方法】
        使用 'w' 模式和 json.dump() 將記憶體中的資料寫入檔案。
        """
        print(f"執行自動儲存...")
        try:
            # 確保目標資料夾存在
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                # 使用 json.dump() 將 self.json_data 寫入檔案 f
                json.dump(self.json_data, f, ensure_ascii=False, indent=4)
            print("儲存成功。")
        except Exception as e:
            print(f"寫入 node_data 失敗: {e}")

    def closeEvent(self, event):
        """在關閉應用程式前，執行最後一次儲存"""
        print("正在關閉應用程式，執行最後儲存...")
        self.save_data()
        super().closeEvent(event)

    def get_node_by_id(self, node_id):
        for node in self.json_data["nodeList"]:
            if node["id"] == node_id:
                return node
        return None

    def update_node_text(self, node_id, new_text):
        node = self.get_node_by_id(node_id)
        if node:
            node["Text"] = new_text
            print(f"資料更新(文字): ID={node_id}")

    def update_node_position(self, node_id, new_pos):
        node = self.get_node_by_id(node_id)
        if node:
            node["coordinate"] = [new_pos.x(), new_pos.y()]
            print(f"資料更新(位置): ID={node_id}")

    def load_nodes_from_data(self):
        """讀取 self.json_data 並在畫布上建立所有節點"""
        for node_data in self.json_data["nodeList"]:
            self.builtRect(node_data["coordinate"][0], node_data["coordinate"][1], node_data=node_data)

    # --- 事件與物件創建方法 ---
    def on_scene_double_click(self, event):
        scene_pos = event.scenePos()
        item = self.scene.itemAt(scene_pos, self.view.transform())
        
        if item is None:
            print("在空白處雙擊，建立新方塊...")
            # 1. 決定新節點的 ID
            new_node_id = (max([n["id"] for n in self.json_data["nodeList"]]) if self.json_data["nodeList"] else 0) + 1
            
            # 2. 建立新節點的資料字典
            new_node_data = {
                "id": new_node_id,
                "Text": rd.choices(summonWorld, weights=probabilities, k=1)[0],
                "FatherNodeid": None,
                "coordinate": [scene_pos.x(), scene_pos.y()]
            }
            
            # 3. 將新資料加入到記憶體中的 self.json_data
            self.json_data["nodeList"].append(new_node_data)
            print(f"資料新增(創建): {new_node_data}")
            
            # 4. 呼叫 builtRect 在畫布上建立視覺物件
            self.builtRect(scene_pos.x(), scene_pos.y(), node_data=new_node_data, edit_on_create=True)
        else:
            QGraphicsScene.mouseDoubleClickEvent(self.scene, event)

    def builtRect(self, posX, posY, node_data, edit_on_create=False):
        # 傳入 ID 和主視窗引用
        rect_item = NodeRectItem(node_data["id"], self, posX - 50, posY - 25, 100, 50)
        
        rect_item.setBrush(QBrush(QColor("#DBDBDB"))) 
        rect_item.setPen(QPen(QColor("#C4C4C4"), 2))
        rect_item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        rect_item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.scene.addItem(rect_item)

        text_on_rect = NodeTextItem(node_data["Text"], parent=rect_item)
        text_on_rect.setDefaultTextColor(QColor("#000000"))
        rect_item.set_text_item(text_on_rect)
        
        # 文字置中
        rect_width = rect_item.rect().width()
        rect_height = rect_item.rect().height()
        text_width = text_on_rect.boundingRect().width()
        text_height = text_on_rect.boundingRect().height()
        center_x = (rect_width - text_width) / 2
        center_y = (rect_height - text_height) / 2
        text_on_rect.setPos(center_x, center_y)

        if edit_on_create:
            text_on_rect.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            text_on_rect.setFocus()
            cursor = text_on_rect.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            text_on_rect.setTextCursor(cursor)

    def reset_todo_dock(self):
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.todo_dock)
        self.todo_dock.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NervePoint()
    window.show()
    sys.exit(app.exec())