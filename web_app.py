# /full/path/to/web_app.py
from flask import Flask, render_template, request, jsonify
# 假設 main.py 與 web_app.py 在同一個資料夾，或者 main.py 所在的路径已加入 sys.path
# 如果 main.py 在不同路徑，你可能需要調整 import 方式，例如：
# import sys
# sys.path.append('/path/to/directory_containing_main_py')
from main import azure_text_to_speech # 這裡的 'main' 是指 main.py 檔案

app = Flask(__name__)

# 定義首頁路由，當使用者訪問根目錄時，顯示 index.html
@app.route('/')
def index():
    return render_template('index.html')

# 定義處理請求的路由，接收來自網頁的 POST 請求
@app.route('/process', methods=['POST'])
def handle_process_request():
    try:
        data = request.get_json() # 取得網頁傳來的 JSON 資料
        input_text = data.get('text', '') # 取得 'text' 欄位的內容

        if not input_text:
            return jsonify(result="請輸入文字內容！"), 400

        audio_data = azure_text_to_speech(input_text) # 呼叫 main.py 中的函式

        # 將音訊資料儲存為 mp3 檔 (可以考慮儲存在 static 資料夾下，如果之後想讓網頁播放)
        output_filename = "output_web.mp3" # 避免與 main.py 直接執行時的檔案衝突
        with open(output_filename, "wb") as f:
            f.write(audio_data)
        return jsonify(result=f"✅ 語音合成成功，已儲存為 {output_filename}")
    except Exception as e:
        return jsonify(error=str(e)), 500 # 如果發生錯誤，回傳錯誤訊息和狀態碼 500

if __name__ == '__main__':
    # 啟動 Flask 開發伺服器
    # debug=True 會在程式碼變動時自動重載，方便開發
    app.run(debug=True)