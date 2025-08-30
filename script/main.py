import json
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
# 往上一層，取得專案的根目錄 (d:\NervePoint)
project_root = os.path.dirname(script_dir)
# 組合出 JSON 檔案的絕對路徑
json_path = os.path.join(project_root, '.json', 'node.json')


with open(json_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)
    
for i in json_data["nodeList"]:
    print(f"節點{i['id']}: \t 文字={i['Text']}\t 父節點={i['FatherNodeid']}\t 座標={i['coordinate']}")