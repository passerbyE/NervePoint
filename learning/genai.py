import google.generativeai as genai

client = genai.client(api_key="AIzaSyD73qU-yigihNqs9h-TtFeLZm_LcZViNLg")
model = genai.GenerativeModel('gemini-2.5-flash')
chat = model.start_chat(history=[])

while True:
    content = input("你: ")
    if content == "": continue
    if content == "end": break
    
    response = chat.send_message(content)
    print("genai: ", response.text)

print(chat.history)