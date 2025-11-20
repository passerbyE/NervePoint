from google import genai

request = ""
outtime = False
client = genai.Client(api_key="AIzaSyCOwpkE4nPRJgcqa8isGTHAA_zQZ9Sbr30")
model="gemini-2.5-flash"

def ask(request, model):
#--- gemini設定 ---
    try:
        response = client.models.generate_content(
            model=model, contents=request
        )
        print(f"{model}回答: {response.candidates[0].content.parts[0].text}")
        return 0
    except Exception as e:
        return e
    

if __name__ == '__main__':
    
    print(f"~~~這裡是大賢者{model}問出你的疑問吧~~~")
    while True:
        if(outtime): request = input("you: ")
        
        if(request == "end"):
            print("結束聊天")
            break
        
        else:
            if ask(request, model) != 0:
                outtime = True
                continue
            else: outtime = False