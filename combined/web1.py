import os
import time
import requests
import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

app = Flask(__name__)

# 載入 .env
load_dotenv()

# Computer Vision 設定
VISION_KEY = os.getenv("VISION_KEY")
VISION_ENDPOINT = os.getenv("VISION_ENDPOINT")

# 初始化 Computer Vision Client
vision_client = ComputerVisionClient(
    VISION_ENDPOINT, CognitiveServicesCredentials(VISION_KEY)
)

# 圖片描述生成
def get_image_description(image_url):
    try:
        description_result = vision_client.describe_image(image_url)
        if description_result.captions:
            return description_result.captions[0].text
        return "未能產生描述"
    except Exception as e:
        return f"取得描述時發生錯誤：{e}"

# 文字識別（OCR）
def get_image_text(image_url):
    try:
        # 執行 OCR 分析
        operation = vision_client.read(image_url, raw=True)
        operation_id = operation.headers["Operation-Location"].split("/")[-1]

        # 等待處理完成
        time.sleep(5)  # 延遲以確保結果準備好

        result = vision_client.get_read_result(operation_id)
        if result.status == "succeeded":
            text = " ".join([line.text for read_result in result.analyze_result.read_results for line in read_result.lines])
            return text if text else "未偵測到文字"
        return "OCR 分析未成功"
    except Exception as e:
        return f"文字識別時發生錯誤：{e}"

# 物件偵測
def get_detected_objects(image_url):
    try:
        # 呼叫 Azure Computer Vision API 進行物件偵測
        objects_result = vision_client.analyze_image(image_url, visual_features=["Objects"])
        
        # 取得所有偵測到的物件
        detected_objects = [
            f"物件：{obj.object_property}（置信度：{obj.confidence:.2%})"
            for obj in objects_result.objects
        ]
        
        # 回傳結果或提示無偵測到物件
        return "\n".join(detected_objects) if detected_objects else "未偵測到物件"
    
    except Exception as e:
        return f"物件偵測時發生錯誤：{e}"
    



# 設定 API 金鑰與端點
FACE_KEY = os.getenv("FACE_KEY")
FACE_ENDPOINT = os.getenv("FACE_ENDPOINT")

# 確保環境變數已設定
if not FACE_KEY or not FACE_ENDPOINT:
    raise ValueError("⚠️ 環境變數 FACE_KEY 或 FACE_ENDPOINT 未設定，請檢查 .env 檔案或系統環境變數。")

def get_detected_faces(image_url):
    """ 使用 Azure Face API 偵測人臉屬性 """
    try:
        # 設定 API URL
        url = f"{FACE_ENDPOINT}/face/v1.0/detect"

        # 設定請求參數（移除已棄用屬性）
        params = {
            "returnFaceAttributes": "headPose,glasses,occlusion,accessories,blur,exposure,noise",
            "recognitionModel": "recognition_04",
            "returnRecognitionModel": "true",
            "detectionModel": "detection_01"
        }

        # 設定請求標頭
        headers = {
            "Ocp-Apim-Subscription-Key": FACE_KEY,
            "Content-Type": "application/json"
        }

        # 設定請求主體
        data = {"url": image_url}

        # 送出 POST 請求
        response = requests.post(url, params=params, headers=headers, json=data)

        # 確保 API 回應成功
        if response.status_code != 200:
            return f"⚠️ API 回應錯誤：{response.status_code} - {response.text}"

        # 解析 API 回應
        faces_result = response.json()

        # 如果沒有偵測到人臉
        if not faces_result:
            return "⚠️ 未偵測到人臉"

        # 提取人臉屬性資訊
        faces_detected = [
            f"眼鏡類型：{face['faceAttributes'].get('glasses', '未知')}，"
            f"模糊程度：{face['faceAttributes'].get('blur', {}).get('blurLevel', '未知')}"
            for face in faces_result
        ]

        return "\n".join(faces_detected)

    except Exception as e:
        return f"⚠️ 人臉偵測時發生錯誤：{e}"





# Flask 處理表單
@app.route("/", methods=["GET", "POST"])
def index():
    description = ""
    image_url = ""
    selected_function = ""

    if request.method == "POST":
        image_url = request.form.get("image_url")
        selected_function = request.form.get("function")

        if image_url and selected_function:
            if selected_function == "describe":
                description = get_image_description(image_url)
            elif selected_function == "ocr":
                description = get_image_text(image_url)
            elif selected_function == "objects":
                description = get_detected_objects(image_url)
            elif selected_function == "faces":
                description = get_detected_faces(image_url)

    return render_template("test.html", description=description, image_url=image_url, selected_function=selected_function)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)