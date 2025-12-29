import sys
import json
import os
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QApplication, QDockWidget, 
    QTreeWidget, QMainWindow, QGraphicsView, QGraphicsScene, 
    QGraphicsRectItem, QTreeWidgetItem, QGraphicsTextItem, 
    QGraphicsLineItem, QLineEdit, QLabel, QPushButton, QTextEdit
)
# 匯入 QAction 以建立選單項目
from PyQt6.QtGui import QColor, QBrush, QPen, QPainter, QAction, QTextCursor, QPolygonF, QCursor, QIcon
from PyQt6.QtCore import Qt, QTimer, QPointF, QLineF
import random as rd
import math 
from google import genai


#--- gemini ---
request = ""
askaskouttime = False
client = genai.Client(api_key="AIzaSyCOwpkE4nPRJgcqa8isGTHAA_zQZ9Sbr30")
model="gemini-2.5-flash"

def ask(request, model):
    """發送請求並回傳 AI 回應文字"""
    try:
        response = client.models.generate_content(
            model=model, contents=request
        )
        # 回傳文字內容
        ai_text = response.candidates[0].content.parts[0].text
        print(f"{model}回答: {ai_text}")
        return ai_text
    except Exception as e:
        print(f"錯誤: {e}")
        return f"錯誤: {str(e)}"


# if __name__ == '__main__':
    
#     print(f"~~~這裡是大賢者{model}問出你的疑問吧~~~")
#     while True:
#         if(askouttime): request = input("you: ")
        
#         if(request == "end"):
#             print("結束聊天")
#             break
        
#         else:
#             if ask(request, model) != 0:
#                 askouttime = True
#                 continue
#             else: askouttime = False



# --- 變數 特殊 設定用 ---
dataUpdateTime = 5000
summonWorld = ["NODE", "(∠ ω< )⌒☆"]
probabilities = [19, 1]



# --- 組合路徑的程式碼 ... ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
json_path = os.path.join(project_root, '.data', 'node.json')


# --- ConnectionLine 類別 ---
class ConnectionLine(QGraphicsLineItem):
    """代表兩個節點之間的連線"""
    def __init__(self, start_item, end_item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        
        self.start_item = start_item
        self.end_item = end_item
        self.arrow_size = 6  # 箭頭大小
        self.arrow_angl = 3
        # 將線條的圖層設定在節點下方 (Z-value < 0)
        self.setZValue(-1)

    # --- 修正 #1：覆寫 boundingRect 方法 ---
    def boundingRect(self):
        """回傳包含線條與箭頭的邊界矩形"""
        extra = (self.pen().width() + self.arrow_size) / 2.0
        return super().boundingRect().adjusted(-extra, -extra, extra, extra)

    # --- 修正 #2：覆寫 paint 方法以繪製箭頭 ---
    def paint(self, painter, option, widget=None):
        """繪製線條與箭頭"""
        # 如果沒有設定畫筆，則不繪製
        if not self.pen():
            return

        painter.setPen(self.pen())
        painter.setBrush(self.pen().color())

        # 取得線條的中心線
        center_line = self.line()
        
        # 繪製主線條
        painter.drawLine(center_line)

        # --- 計算並繪製箭頭 ---
        # 取得線條終點和角度
        end_point = center_line.p2()
        angle = math.atan2(-center_line.dy(), center_line.dx())

        # 計算箭頭的兩個頂點
        arrow_p1 = end_point + QPointF(math.sin(angle - math.pi / self.arrow_angl) * self.arrow_size,
                                       math.cos(angle - math.pi / self.arrow_angl) * self.arrow_size)
        arrow_p2 = end_point + QPointF(math.sin(angle - math.pi + math.pi / self.arrow_angl) * self.arrow_size,
                                       math.cos(angle - math.pi + math.pi / self.arrow_angl) * self.arrow_size)

        # 建立箭頭的多邊形
        arrow_head = QPolygonF([end_point, arrow_p1, arrow_p2])
        
        # 繪製並填滿箭頭
        painter.drawPolygon(arrow_head)


    def update_positions(self):
        """根據節點中心點更新線條的起點和終點"""
        start_pos = self.start_item.scenePos() + self.start_item.rect().center()
        
        # --- 修正 #1：計算與目標方塊邊緣的交點作為終點 ---
        end_pos = self.get_intersection_point(self.end_item, start_pos)

        self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())

    # --- 修正 #2：新增計算交點的輔助方法 ---
    def get_intersection_point(self, target_node, start_pos):
        """計算從 start_pos 到 target_node 中心的連線與其邊界的交點"""
        target_center = target_node.scenePos() + target_node.rect().center()
        
        # 如果起點和終點太近，直接回傳終點中心以避免計算錯誤
        if (target_center - start_pos).manhattanLength() < 1:
            return target_center

        # 建立一條從起點到目標中心的線
        line = QLineF(start_pos, target_center)
        
        # 取得目標節點在場景中的邊界
        target_rect = target_node.sceneBoundingRect()

        # 取得目標節點的四個邊
        top_line = QLineF(target_rect.topLeft(), target_rect.topRight())
        right_line = QLineF(target_rect.topRight(), target_rect.bottomRight())
        bottom_line = QLineF(target_rect.bottomRight(), target_rect.bottomLeft())
        left_line = QLineF(target_rect.bottomLeft(), target_rect.topLeft())

        # --- 修正：使用 PyQt6 的 intersects 語法 ---
        # 依序檢查與四個邊的交點
        intersection_type, intersect_point = line.intersects(top_line)
        if intersection_type == QLineF.IntersectionType.BoundedIntersection:
            return intersect_point
        
        intersection_type, intersect_point = line.intersects(right_line)
        if intersection_type == QLineF.IntersectionType.BoundedIntersection:
            return intersect_point
            
        intersection_type, intersect_point = line.intersects(bottom_line)
        if intersection_type == QLineF.IntersectionType.BoundedIntersection:
            return intersect_point
            
        intersection_type, intersect_point = line.intersects(left_line)
        if intersection_type == QLineF.IntersectionType.BoundedIntersection:
            return intersect_point

        # 如果沒有找到交點（例如起點在方塊內部），則回傳中心點
        return target_center


class NodeTextItem(QGraphicsTextItem):
    """自訂的文字項目，處理編輯邏輯"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        #文字大小變更事件
        self.document().contentsChange.connect(self.on_text_changed)
        
    def on_text_changed(self):
        parent_rect = self.parentItem()
        if parent_rect and hasattr(parent_rect, 'adjust_size_to_text'):
            parent_rect.adjust_size_to_text()
        
    
    def focusOutEvent(self, event):
        # 當文字失去焦點時 (編輯完成)，設回不可編輯狀態
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        #取消反白
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)  
        
        # 呼叫父類別的方法
        super().focusOutEvent(event)

        # 取得父項目 (NodeRectItem)
        parent_rect = self.parentItem()
        if parent_rect and hasattr(parent_rect, 'this_node_id'):
            node_id_to_update = parent_rect.this_node_id
            new_text = self.toPlainText()
            print(f"文字編輯完成，ID: {node_id_to_update}, 新內容: {new_text}")

            # 更新全域 node_data 中的資料
            for node in node_data["nodeList"]:
                if node["id"] == node_id_to_update:
                    node["Text"] = new_text
                    print(f"節點 {node_id_to_update} 的資料已更新。")
                    break


class NodeRectItem(QGraphicsRectItem):
    """自訂的方塊項目，處理雙擊事件"""
    def __init__(self,this_node_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_item = None # 用來存放對應的文字項目
        self.this_node_id = this_node_id
        # --- 修正 #2：新增列表來追蹤連線 ---
        self.connections = []

    def add_connection(self, connection):
        """新增一條連線到此節點的追蹤列表"""
        self.connections.append(connection)

    def remove_connection(self, connection):
        """從追蹤列表中移除一條連線"""
        if connection in self.connections:
            self.connections.remove(connection)

    def set_text_item(self, text_item):
        self.text_item = text_item

    def adjust_size_to_text(self):
        
        
        h = 20
        v = 10
        
        text_rect = self.text_item.boundingRect()
        print(f"大小: {text_rect}")
        new_width = text_rect.width() + h *2
        new_height = text_rect.height() + v *2
        min_width = 100
        min_height = 50
        new_width = max(new_width, min_width)
        new_height = max(new_height, min_height)
        
        current_center = self.scenePos() + self.rect().center()

        # 計算新的左上角座標
        new_x = current_center.x() - new_width / 2
        new_y = current_center.y() - new_height / 2

        # 更新方塊的位置和大小
        self.setPos(new_x, new_y)
        self.setRect(0, 0, new_width, new_height)

        # 文字本身不需要移動，因為它的座標是相對於方塊的
        # 但我們需要重新置中它
        self.text_item.setPos(
            (new_width - text_rect.width()) / 2,
            (new_height - text_rect.height()) / 2
        )
        
        for node in node_data["nodeList"]:
                if node["id"] == self.this_node_id:
                    # 取得方塊的寬度和高度
                    width = self.rect().width()
                    height = self.rect().height()
                    node["coordinate"] = [
                        node["coordinate"][0],
                        node["coordinate"][1],
                        width,
                        height
                    ]
                    break
        
        
    def mouseDoubleClickEvent(self, event):
        # 當方塊被雙擊時，讓其內部的文字進入編輯模式
        if self.text_item:
            # 儲存方塊目前的中心點
            self.original_center = self.scenePos() + self.rect().center()
            
            self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.text_item.setFocus()
            # 選取所有文字
            cursor = self.text_item.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            self.text_item.setTextCursor(cursor)
        # 呼叫父類別的方法，以防有其他預設行為
        super().mouseDoubleClickEvent(event)

    def itemChange(self, change, value):
        # 檢查位置是否已變更
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged and self.scene():
            # --- 修正 #3：更新所有相連的線條 ---
            for conn in self.connections:
                conn.update_positions()

            # 當位置移動完成後觸發
            new_pos = value # value 是新的 QPointF 位置
            
            # 尋找對應的
            # 尋找對應的節點資料並更新
            for node in node_data["nodeList"]:
                if node["id"] == self.this_node_id:
                    # 取得方塊的寬度和高度
                    width = self.rect().width()
                    height = self.rect().height()
                    
                    # 更新座標，我們儲存中心點座標以保持一致
                    center_x = new_pos.x() + width / 2
                    center_y = new_pos.y() + height / 2
                    
                    node["coordinate"] = [
                        center_x,
                        center_y,
                        width,
                        height
                    ]
                    break
        
        
                    
        return super().itemChange(change, value)



# --- 新增：FloatingChatWindow 類別（移到這裡）---
class FloatingChatWindow(QWidget):
    """浮動在滑鼠右上角的聊天視窗"""
    
    def __init__(self, parent=None, node_id=None, gemini_model=None):
        super().__init__(parent)
        
        self.node_id = node_id
        self.gemini_model = gemini_model
        self.chat_session = None
        self.parent_window = parent  # 儲存父視窗參考
        
        # --- 新增：從 node_data 載入聊天歷史 ---
        self.chat_history = self.load_chat_history()
        
        # 建立對話工作階段
        if self.gemini_model:
            self.chat_session = self.gemini_model.start_chat(history=[])
        
        # --- 修正：強制設定視窗大小 ---
        self.setFixedSize(350, 400)
        
        # 設定視窗樣式
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # 使浮動視窗可拖曳（在標題欄拖動）
        self._drag_active = False
        self._drag_offset = None
        self._drag_title_height = 40  # 點擊此高度範圍內可拖動視窗

        def _mousePressEvent(event):
            # 只在左鍵且點擊標題欄範圍時開始拖曳
            if event.button() == Qt.MouseButton.LeftButton:
                # 使用 local position 檢查是否點在標題欄（避免在輸入欄拖動）
                pos = event.position()
                if pos.y() <= self._drag_title_height:
                    self._drag_active = True
                    # globalPosition 為 QPointF，轉成 QPoint 以便計算
                    self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    event.accept()
                    return
            return QWidget.mousePressEvent(self, event)

        def _mouseMoveEvent(event):
            if self._drag_active:
                new_top_left = event.globalPosition().toPoint() - self._drag_offset
                self.move(new_top_left)
                event.accept()
                return
            return QWidget.mouseMoveEvent(self, event)

        def _mouseReleaseEvent(event):
            if event.button() == Qt.MouseButton.LeftButton and self._drag_active:
                self._drag_active = False
                self._drag_offset = None
                event.accept()
                return
            return QWidget.mouseReleaseEvent(self, event)

        # 綁定到這個實例（以覆寫預設事件處理）
        self.mousePressEvent = _mousePressEvent
        self.mouseMoveEvent = _mouseMoveEvent
        self.mouseReleaseEvent = _mouseReleaseEvent
        
        # 建立主佈局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        
        # === 標題欄 ===
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 8, 10, 8)
        
        node_text = next((n.get("Text", "") for n in node_data["nodeList"] if n.get("id") == node_id), None)
        if not node_text:
            node_text = f"節點 {node_id}"
        else:
            node_text = node_text.strip()
            if len(node_text) > 30:
                node_text = node_text[:27] + "..."
        title_label = QLabel(f"與「{node_text}」聊天")
        title_label.setStyleSheet("""
            color: #D4D4D4; 
            font-weight: bold; 
            font-size: 12px;
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 關閉按鈕
        close_button = QPushButton("×")
        close_button.setMaximumWidth(25)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #D4D4D4;
                border: none;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E81123;
                color: #FFFFFF;
            }
        """)
        close_button.clicked.connect(self.hide)
        title_layout.addWidget(close_button)
        
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        title_widget.setStyleSheet("background-color: #2D2D30;")
        main_layout.addWidget(title_widget)
        
        # === 訊息顯示區域 ===
        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        self.message_display.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: none;
                padding: 10px;
                font-size: 11px;
            }
            QScrollBar:vertical {
                border: none;
                background: #252526;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #606060;
                min-height: 20px;
                border-radius: 4px;
            }
        """)
        main_layout.addWidget(self.message_display)
        
        # === 輸入區域 ===
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 5, 10, 10)
        input_layout.setSpacing(5)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("輸入訊息...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2D2D30;
                color: #D4D4D4;
                border: 1px solid #4b4b4b;
                padding: 6px;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 1px solid #007ACC;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        send_button = QPushButton("發送")
        send_button.setMaximumWidth(60)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: #FFFFFF;
                border: none;
                padding: 6px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0098FF;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
        """)
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)
        
        input_widget = QWidget()
        input_widget.setLayout(input_layout)
        input_widget.setStyleSheet("background-color: #252526;")
        main_layout.addWidget(input_widget)
        
        self.setLayout(main_layout)
        
        # 整體樣式
        self.setStyleSheet("""
            FloatingChatWindow {
                background-color: #252526;
                border: 2px solid #007ACC;
                border-radius: 5px;
            }
        """)
        
        # --- 新增：在視窗建立完成後，載入並顯示歷史訊息 ---
        self.display_chat_history()
    
    # --- 新增：載入聊天歷史 ---
    def load_chat_history(self):
        """從 node_data 載入此節點的聊天歷史"""
        for node in node_data["nodeList"]:
            if node["id"] == self.node_id:
                # 如果節點有 chat_history 欄位，就載入；否則回傳空列表
                return node.get("chat_history", [])
        return []
    
    # --- 新增：顯示歷史訊息 ---
    def display_chat_history(self):
        """將載入的聊天歷史顯示在視窗中"""
        for msg in self.chat_history:
            role = msg.get("role", "user")
            text = msg.get("text", "")
            
            if role == "user":
                self.display_message(f"你: {text}", color="#007ACC")
            elif role == "ai":
                self.display_message(f"AI: {text}", color="#4EC9B0")
    
    # --- 新增：儲存聊天歷史到 node_data ---
    def save_chat_history(self):
        """將聊天歷史儲存到 node_data 並寫入 JSON"""
        for node in node_data["nodeList"]:
            if node["id"] == self.node_id:
                node["chat_history"] = self.chat_history
                break
        
        # 呼叫父視窗的 save_data 方法
        if self.parent_window and hasattr(self.parent_window, 'save_data'):
            self.parent_window.save_data()
    
    def send_message(self):
        """發送訊息到 AI"""
        user_text = self.input_field.text().strip()
        if not user_text:
            return
        
        # --- 新增：將使用者訊息加入歷史 ---
        self.chat_history.append({"role": "user", "text": user_text})
        
        # 顯示使用者訊息
        self.display_message(f"你: {user_text}", color="#007ACC")
        self.input_field.clear()
        
        # 如果沒有 Gemini 模型，只顯示訊息
        if not self.chat_session:
            ai_response = "AI: 無法連接到 AI 模型"
            self.display_message(ai_response, color="#F48771")
            # 也要儲存錯誤訊息
            self.chat_history.append({"role": "ai", "text": ai_response})
            self.save_chat_history()
            return
        
        # 發送訊息到 AI 並顯示回應
        try:
            self.input_field.setEnabled(False)
            self.display_message("AI: 思考中...", color="#808080")
            
            response = self.chat_session.send_message(user_text)
            
            # 移除 "思考中..." 的訊息
            cursor = self.message_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()
            
            # 取得 AI 回應文字
            ai_text = response.text
            
            # --- 新增：將 AI 回應加入歷史 ---
            self.chat_history.append({"role": "ai", "text": ai_text})
            
            # 顯示 AI 回應
            self.display_message(f"AI: {ai_text}", color="#4EC9B0")
            
            # --- 新增：儲存聊天歷史 ---
            self.save_chat_history()
            
            self.input_field.setEnabled(True)
            self.input_field.setFocus()
        except Exception as e:
            error_msg = f"發生錯誤 - {str(e)}"
            
            # --- 新增：錯誤訊息也要儲存 ---
            self.chat_history.append({"role": "ai", "text": error_msg})
            
            self.display_message(f"AI: {error_msg}", color="#F48771")
            
            # --- 新增：儲存聊天歷史 ---
            self.save_chat_history()
            
            self.input_field.setEnabled(True)
    
    # display_message 和 show_at_mouse 保持不變
    def display_message(self, message, color="#D4D4D4"):
        """將訊息顯示在聊天區域"""
        cursor = self.message_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.message_display.setTextCursor(cursor)
        
        self.message_display.setTextColor(QColor(color))
        self.message_display.append(message)
        
        # 自動滾動到最下方
        scrollbar = self.message_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def show_at_mouse(self):
        """在滑鼠右上角顯示此視窗"""
        cursor_pos = QCursor.pos()
        x = cursor_pos.x() + 15
        y = cursor_pos.y() - 10
        self.move(x, y)
        self.show()
        self.input_field.setFocus()


# --- NervePoint 類別（現在在 FloatingChatWindow 之後）---
class NervePoint(QMainWindow):
    def __init__(self):
        super().__init__()

        
        #讀取節點資料
        global node_data
        node_data = self.load_data()
        
        # --- 插入到json檔案用來設置的 ---
        self.newest_id = node_data["newest_id"]
        
        # --- 繪圖與互動狀態變數 ---
        self.onitem = None # 滑鼠目前懸停的物件
        self.start_node_item = None # 畫線的起始節點
        self.preview_line = None # 預覽線條物件
        
        # --- 新增：初始化 Gemini AI 模型 ---
        try:
            import google.generativeai as genai
            genai.configure(api_key="AIzaSyCOwpkE4nPRJgcqa8isGTHAA_zQZ9Sbr30")
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )
            print("✓ Gemini AI 模型已成功載入")
        except Exception as e:
            print(f"✗ Gemini AI 模型載入失敗: {e}")
            self.model = None
        
        # --- 新增：浮動聊天視窗 ---
        self.floating_chat = None
        
        #儲存用timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.save_data)
        self.timer.start(dataUpdateTime)
        
        # 參數
        self.lastDockChange = True # 初始化 lastDockChange 屬性
        
        self.setWindowTitle("NervePoint")
        self.setGeometry(560, 240, 800, 600)
        
        # --- 全域樣式設定 ---
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
                color: #D4D4D4; 
            }
            QDockWidget::title {
                background-color: #353535;
                color: #D4D4D4;
                text-align: Left;
                padding: 4px;
            }
            QTreeWidget {
                background-color: #252525;
                color: #D4D4D4;
                border: none;
                font-size: 14px;
            }
            QTreeWidget::item:hover {
                background-color: #3b3b3b;
            }
            QTreeWidget::item:selected {
                background-color: #4b4b4b;
                color: white;
            }
        """)

        # --- 創建todo 物件 ---
        todo_container = QWidget()
        todo_layout = QVBoxLayout()
        self.todo_tree = QTreeWidget()
        self.todo_tree.setHeaderHidden(True)
        task1 = QTreeWidgetItem(self.todo_tree, ["點擊空白區域新增節點", "-1"])
        
        subTake1 = QTreeWidgetItem(task1, ["完成?", "-1"])
        
        self.todo_tree.resizeColumnToContents(0)
        self.todo_tree.resizeColumnToContents(1)
        todo_layout.addWidget(self.todo_tree)
        todo_container.setLayout(todo_layout)
        self.todo_dock.setWidget(todo_container)
        
        #初始並創建todo 的 dock 到左側
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.todo_dock)
        
        self.todo_tree.doubleClicked.connect(self.todoTree_clicked)
        
        # --- 步驟 1: 初始化狀態列 ---
        # 取得或建立一個狀態列，並設定其樣式
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("background-color: #353535; color: #D4D4D4;")

        # 這裡是所有圖形項目的容器
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QColor("#181818"))

        # --- 綁定正確的滑鼠事件 ---
        self.scene.mouseDoubleClickEvent = self.on_scene_double_click
        self.scene.mousePressEvent = self.scene_mouse_press
        self.scene.mouseMoveEvent = self.scene_mouse_move
        self.scene.mouseReleaseEvent = self.scene_mouse_release

        # 3. 建立一個 QGraphicsView (檢視/視窗)
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing) # 反鋸齒
        
        
        # --- 自訂捲動軸樣式 ---
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
        self.view.verticalScrollBar().setStyleSheet(stylesheet)
        self.view.horizontalScrollBar().setStyleSheet(stylesheet)
        
    
    # --- 步驟 2: 建立一個顯示通知的函式 ---
    def show_notification(self, message, timeout=3000):
        """
        在視窗底部的狀態列顯示一條訊息，並在指定時間後自動消失。
        :param message: 要顯示的字串訊息。
        :param timeout: 訊息顯示的毫秒數 (預設為 3000ms = 3秒)。
        """
        self.status_bar.showMessage(message, timeout)


    def updateTree(self):
        self.todo_tree.clear()
        # 建立一個字典來快速查找父節點
        tree_items = {}
        # 先創建所有節點的 QTreeWidgetItem
        for node_info in node_data["nodeList"]:
            # 使用 node_info 的 id 作為第二欄的資料，方便後續查找
            item = QTreeWidgetItem([node_info["Text"], str(node_info["id"])])
            tree_items[node_info["id"]] = item

        # 遍歷所有節點來建立父子關係
        for node_info in node_data["nodeList"]:
            item = tree_items[node_info["id"]]
            parent_id = node_info["FatherNodeid"]

            if parent_id != -1 and parent_id in tree_items:
                # 如果有父節點，將其添加到父節點下
                parent_item = tree_items[parent_id]
                parent_item.addChild(item)
            else:
                # 如果沒有父節點，將其添加到樹的根部
                self.todo_tree.addTopLevelItem(item)
                
                
    def todoTree_clicked(self, event):
        
        tree_item = self.todo_tree.itemFromIndex(event)
        if not tree_item or not tree_item.text(1):
            return
        
        #要先完成底層任務才能往上做
        if tree_item.childCount() > 0:
            return

        try:
            node_id_to_delete = int(tree_item.text(1))
        except (ValueError, TypeError):
            print(f"無效的節點 ID: {tree_item.text(1)}")
            return

        print(f"從樹狀圖請求刪除節點 ID: {node_id_to_delete}")

        # --- 尋找場景中對應的 NodeRectItem ---
        node_to_delete = None
        for item in self.scene.items():
            if isinstance(item, NodeRectItem) and item.this_node_id == node_id_to_delete:
                node_to_delete = item
                break

        if node_to_delete:
            # --- 套用與 keyPressEvent 相同的刪除邏輯 ---
            # 建立一個要迭代的連線副本，因為會在迴圈中修改原始列表
            for conn in list(node_to_delete.connections):
                # 找到這條線連接的另一個節點
                other_node = conn.start_item if conn.end_item == node_to_delete else conn.end_item
                
                # 讓另一個節點忘記這條線
                if other_node:
                    other_node.remove_connection(conn)
                
                # 從場景中移除線條圖形
                self.scene.removeItem(conn)
                print(f"已移除連接到節點 {node_id_to_delete} 的線條。")

            # 從 scene 中移除圖形項目 (包含其子項目，如文字)
            self.scene.removeItem(node_to_delete)

            # 從 node_data["nodeList"] 中移除對應的資料
            node_data["nodeList"] = [
                node for node in node_data["nodeList"] 
                if node["id"] != node_id_to_delete
            ]
            
            print(f"節點 {node_id_to_delete} 已被刪除。")

            # 如果被刪除的節點剛好是 onitem，則清除參考
            if self.onitem == node_to_delete:
                self.onitem = None
            
            self.show_notification(f"恭喜完成工作: {tree_item.text(0)} 辛苦了 !!!!")
            # 更新樹狀圖並儲存
            self.save_data()
            self.updateTree()
            
        else:
            print(f"錯誤：在場景中找不到 ID 為 {node_id_to_delete} 的節點圖形。")
            
    
    # 鍵盤事件
    def keyPressEvent(self, event):
        keycode = event.key()
        print(f"按鍵: {keycode}")
        match keycode:
            case 67:  # C 鍵 - 開啟聊天視窗
                print(f"按下 C 鍵, onitem = {self.onitem}, 類型 = {type(self.onitem)}")
                if self.onitem and isinstance(self.onitem, NodeRectItem):
                    print(f"準備開啟節點 {self.onitem.this_node_id} 的聊天視窗")
                    if self.floating_chat is None or self.floating_chat.node_id != self.onitem.this_node_id:
                        self.floating_chat = FloatingChatWindow(
                            parent=self,
                            node_id=self.onitem.this_node_id,
                            gemini_model=self.model  # 傳遞 gemini_model
                        )
                    self.floating_chat.show_at_mouse()
                else:
                    print("沒有選中有效的節點")
                    
            case 16777223: # del刪除節點
                print("刪除")
                
                if self.onitem and isinstance(self.onitem, NodeRectItem):
                    node_to_delete = self.onitem # 使用一個更清晰的變數名稱
                    node_id_to_delete = node_to_delete.this_node_id
                    print(f"準備刪除節點 ID: {node_id_to_delete}")
                    

                    # --- 修正：在刪除節點前，先處理與其相連的線條 ---
                    # 建立一個要迭代的連線副本，因為我們會在迴圈中修改原始列表
                    for conn in list(node_to_delete.connections):
                        # 找到這條線連接的另一個節點
                        other_node = conn.start_item if conn.end_item == node_to_delete else conn.end_item
                        
                        # 讓另一個節點忘記這條線
                        if other_node:
                            other_node.remove_connection(conn)
                        
                        # 從場景中移除線條圖形
                        self.scene.removeItem(conn)
                        print(f"已移除連接到節點 {node_id_to_delete} 的線條。")

                    # 從 scene 中移除圖形項目
                    self.scene.removeItem(node_to_delete)

                    # 從 node_data["nodeList"] 中移除對應的資料
                    node_data["nodeList"] = [
                        node for node in node_data["nodeList"] 
                        if node["id"] != node_id_to_delete
                    ]
                    
                    print(f"節點 {node_id_to_delete} 已被刪除。")

                    # --- 在刪除成功後呼叫通知 ---
                    self.show_notification(f"節點 {node_id_to_delete} 已刪除")

                    # 清除 onitem 參考
                    self.onitem = None
                
                self.updateTree()
                    
                    
            case 16777216: #esc 刪除json 資料 測試用
                print("清除json資料")
                node_data["nodeList"] = []
                node_data["newest_id"] = 0
                
            case 16777219: #back 用來測試的
                self.updateTree()

    # --- 滑鼠事件處理 ---
    def scene_mouse_press(self, event):
        """處理場景中的滑鼠按下事件"""
        scene_pos = event.scenePos()
        item = self.scene.itemAt(scene_pos, self.view.transform())

        if isinstance(item, NodeTextItem):
            item = item.parentItem()

        if event.button() == Qt.MouseButton.RightButton and isinstance(item, NodeRectItem):
            self.start_node_item = item
            line_pen = QPen(QColor("#E9E9E9"), 2, Qt.PenStyle.DashLine)
            start_pos = self.start_node_item.scenePos() + self.start_node_item.rect().center()
            self.preview_line = self.scene.addLine(
                start_pos.x(), start_pos.y(),
                scene_pos.x(), scene_pos.y(),
                line_pen
            )
            print(f"開始從節點 {self.start_node_item.this_node_id} 畫線...")
        else:
            QGraphicsScene.mousePressEvent(self.scene, event)

    def scene_mouse_move(self, event):
        """處理場景中的滑鼠移動事件"""
        scene_pos = event.scenePos()
        self.onitem = self.scene.itemAt(scene_pos, self.view.transform())
        if self.onitem and isinstance(self.onitem, NodeTextItem):
            self.onitem = self.onitem.parentItem()

        if self.preview_line:
            line = self.preview_line.line()
            line.setP2(event.scenePos())
            self.preview_line.setLine(line)
        else:
            QGraphicsScene.mouseMoveEvent(self.scene, event)

    def scene_mouse_release(self, event):
        """處理場景中的滑鼠釋放事件"""
        line_pen = QPen(QColor("#E9E9E9"), 2, Qt.PenStyle.SolidLine)
        
        if self.start_node_item and self.preview_line:
            scene_pos = event.scenePos()
            self.preview_line.hide()
            end_item = self.scene.itemAt(scene_pos, self.view.transform())
            self.preview_line.show()

            if isinstance(end_item, NodeTextItem):
                end_item = end_item.parentItem()

            if isinstance(end_item, NodeRectItem) and end_item is not self.start_node_item:
                print(f"成功連接節點 {self.start_node_item.this_node_id} 到 {end_item.this_node_id}")
                
                # --- 修正 #4：處理覆蓋舊連線的邏輯 ---
                # 檢查起始節點是否已經有一條作為"起點"的連線
                connection_to_remove = None
                for conn in self.start_node_item.connections:
                    # 如果這條線的起點是我們現在的起始節點，就表示要替換它
                    if conn.start_item == self.start_node_item:
                        connection_to_remove = conn
                        break
                
                if connection_to_remove:
                    print(f"節點 {self.start_node_item.this_node_id} 的舊連線已被移除。")
                    # 從舊的父節點的追蹤中移除
                    connection_to_remove.end_item.remove_connection(connection_to_remove)
                    # 從場景中刪除線條圖形
                    self.scene.removeItem(connection_to_remove)
                    # 從子節點的追蹤中移除
                    self.start_node_item.remove_connection(connection_to_remove)


                # --- 修正 #5：使用新的 ConnectionLine 類別 ---
                connection_line = ConnectionLine(self.start_node_item, end_item)
                connection_line.setPen(line_pen) # 正確的設定方式
                connection_line.update_positions() # 初始對齊
                self.scene.addItem(connection_line)

                # 讓節點追蹤這條新連線
                self.start_node_item.add_connection(connection_line)
                end_item.add_connection(connection_line)
                
                # 更新資料模型
                for node in node_data["nodeList"]:
                    if node["id"] == self.start_node_item.this_node_id:
                        node["FatherNodeid"] = end_item.this_node_id
                        break
                
            else:
                print("取消連線。")

            self.scene.removeItem(self.preview_line)
            self.preview_line = None
            self.start_node_item = None
        
        QGraphicsScene.mouseReleaseEvent(self.scene, event)
        self.save_data()
        self.updateTree()
        self.todo_tree.expandAll() 

    #雙擊事件
    def on_scene_double_click(self, event):
        scene_pos = event.scenePos()
        item = self.scene.itemAt(scene_pos, self.view.transform())
        
        if item is None:
            print("在空白處雙擊，建立新方塊...")
            self.builtRect(scene_pos.x(), scene_pos.y())
        else:
            print("在現有項目上雙擊")
            QGraphicsScene.mouseDoubleClickEvent(self.scene, event)


    # 設置分塊
    def builtRect(self, posX, posY):
        rect_item = NodeRectItem(self.newest_id, 0, 0, 100, 50)
        rect_item.setPos(posX - 50, posY - 25)
        
        rect_item.setBrush(QBrush(QColor("#DBDBDB"))) 
        rect_item.setPen(QPen(QColor("#C4C4C4"), 2))
        rect_item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        rect_item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.scene.addItem(rect_item)

        text_on_rect = NodeTextItem(rd.choices(summonWorld, weights=probabilities, k=1)[0], parent=rect_item)
        text_on_rect.setDefaultTextColor(QColor("#000000"))
        
        rect_item.set_text_item(text_on_rect)
        
        rect_item.adjust_size_to_text()

        text_on_rect.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        text_on_rect.setFocus()
        cursor = text_on_rect.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        text_on_rect.setTextCursor(cursor)
        
        new_node_data = {"id": self.newest_id,
                        "Text": text_on_rect.toPlainText(),
                        "FatherNodeid": -1,
                        "coordinate": [
                            posX,
                            posY,
                            rect_item.rect().width(),
                            rect_item.rect().height()
                        ]}
        node_data["nodeList"].append(new_node_data)
        self.newest_id += 1
        node_data["newest_id"] = self.newest_id
        self.save_data()


    # --- 視窗與資料方法 ---
    def reset_todo_dock(self):
        print("執行復位側邊欄...")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.todo_dock)
        self.todo_dock.show()
        
    def load_data(self):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"成功從 {json_path} 讀取資料。")
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"警告：找不到或無法解析 {json_path}。將使用預設空資料。")
            return {"projectName": "test", "newest_id": 1, "nodeList": []}

    def save_data(self):
        try:
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(node_data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"寫入 node_data 失敗: {e}")

    def closeEvent(self, event):
        """在關閉應用程式前，執行最後一次儲存"""
        print("正在關閉應用程式，執行最後儲存...")
        self.save_data()
        super().closeEvent(event)

    def load_nodes_from_data(self):
        for node_info in node_data["nodeList"]:
            # 這裡需要一個更完整的 builtRect 版本來處理載入
            # 暫時跳過以避免錯誤
            pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NervePoint()
    window.show()
    sys.exit(app.exec())
