import os # 匯入 os 模組用於路徑操作
import time # 匯入 time 模組用於產生時間戳記
from flask import Flask, render_template, request, jsonify, url_for 

import requests
import io
from playsound import playsound  # 安裝方式：pip install playsound==1.2.2

# Azure 語音合成函式
def azure_text_to_speech(text):
    subscription_key = "BRjihnIspO9Ntn3NaCd9bTMwZI2JGD5t6Ihp3WQGDHMyrlTNeOmQJQQJ99BEACYeBjFXJ3w3AAAYACOGy2X0"
    region = "eastus"
    endpoint = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"

    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
        "User-Agent": "python-client"
    }
    ssml = f"""
    <speak version='1.0' xml:lang='zh-TW'>
        <voice xml:lang='zh-TW' xml:gender='Female' name='zh-TW-HsiaoChenNeural'>
            {text}
        </voice>
    </speak>
    """
    response = requests.post(endpoint, headers=headers, data=ssml.encode("utf-8"))

    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"語音合成失敗：{response.status_code} - {response.text}")






app = Flask(__name__)

# 設定靜態檔案夾，雖然 Flask 預設就是 'static'，明確寫出有助於理解
app.static_folder = 'static'

# 定義首頁路由，當使用者訪問根目錄時，顯示 index.html
@app.route('/')
def index():
    return render_template('index.html')

# 定義處理請求的路由，接收來自網頁的 POST 請求
@app.route('/process', methods=['POST'])
def handle_process_request():
    try:
        data = request.get_json() # 正確獲取前端傳來的 JSON 資料
        input_text = data.get('text', '')

        if not input_text:
            return jsonify(error="請輸入文字內容！"), 400

        # 確保 static 資料夾存在
        static_dir = os.path.join(app.root_path, app.static_folder)
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)

        audio_data = azure_text_to_speech(input_text) # 呼叫 main.py 中的函式

        # 將音訊資料儲存為 mp3 檔到 static 資料夾
        # 使用一個固定的檔案名稱，或者考慮使用更複雜的方式避免衝突（例如基於時間戳或使用者 ID）
        output_filename_on_server = "output_speech.mp3" # 儲存在 static 資料夾中的檔案名稱
        audio_file_path = os.path.join(static_dir, output_filename_on_server)

        with open(audio_file_path, "wb") as f:
            f.write(audio_data)
        audio_url = url_for('static', filename=output_filename_on_server, v=int(time.time()), _external=False) # 生成公開網址並加上時間戳記
        return jsonify(message="✅ 語音合成成功！", audio_url=audio_url) # 回傳訊息和音訊網址
    except Exception as e:
        return jsonify(error=f"處理時發生錯誤：{str(e)}"), 500 # 如果發生錯誤，回傳錯誤訊息和狀態碼 500

if __name__ == '__main__':
    # 啟動 Flask 開發伺服器
    # debug=True 會在程式碼變動時自動重載，方便開發
    app.run(debug=True)