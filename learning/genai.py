import google.generativeai as genai
genai.configure(api_key="AIzaSyD73qU-yigihNqs9h-TtFeLZm_LcZViNLg")
system_instruction = "你是一位知識淵博、風趣幽默的總結人員。請用生動有趣的方式回答所有問題，並在適當的時候加入一些題目相關的冷知識。"

model = genai.GenerativeModel(
    model_name="gemini-2.5-pro-latest",
    system_instruction=system_instruction
)

# --- 2. 建立一個會自動記錄對話的 ChatSession ---
# history=[] 表示從一個全新的對話開始
chat = model.start_chat(history=[])

print("--- 已啟動與歷史學家的對話 ---")
print("輸入 'end' 結束聊天，輸入 'history' 查看對話紀錄。")

while True:
    content = input("你: ")
    if content.lower() == "end":
        break
    if content.lower() == 'history':
        # 方便除錯，查看目前的對話紀錄
        print("--- 對話紀錄 ---")
        for message in chat.history:
            print(f"[{message.role}]: {message.parts[0].text}")
        print("-----------------")
        continue

    print("(思考中...): ", end="", flush=True)
    
    # --- 3. 發送訊息，ChatSession 會自動附上歷史紀錄 ---
    response = chat.send_message(content)
    
    # 清除 "思考中..." 的提示並輸出回應
    print("\r" + " " * 25 + "\r", end="") 
    print("回答: ", response.text, flush=True)

print("結束聊天")