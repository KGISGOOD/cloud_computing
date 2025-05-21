import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
import requests
import time

app = Flask(__name__)

# 載入 .env
load_dotenv()

# Computer Vision 設定
VISION_KEY = os.getenv("VISION_KEY")
VISION_ENDPOINT = os.getenv("VISION_ENDPOINT")

# Translator 設定（與其他資料夾一致）
KEY = os.getenv("KEY")
REGION = os.getenv("REGION")
ENDPOINT = os.getenv("ENDPOINT")

# 初始化 Computer Vision Client
vision_client = ComputerVisionClient(
    VISION_ENDPOINT, CognitiveServicesCredentials(VISION_KEY)
)


translator_client = TextTranslationClient(
    endpoint=ENDPOINT,
    credential=TranslatorCredential(KEY, REGION)
)


def translate_text(text, src_language, dst_language):
    try:
        targets = [InputTextItem(text=text)]
        responses = translator_client.translate(
            content=targets,
            to=[dst_language],
            from_parameter=src_language
        )
        return responses[0].translations[0].text
    except Exception as e:
        return f"翻譯時發生錯誤：{e}"


# 圖片描述生成
def get_image_description(image_url):
    try:
        description_result = vision_client.describe_image(image_url)
        if description_result.captions:
            return description_result.captions[0].text
        return "未能產生描述"
    except Exception as e:
        return "無法讀取圖片，請換一張"

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
            return text if text else "No text detected"  # 改為英文
        return "OCR analysis was not successful"  # 改為英文
    except Exception as e:
        return "無法讀取圖片，請換一張"

# 物件偵測
def get_detected_objects(image_url):
    try:
        # 呼叫 Azure Computer Vision API 進行物件偵測
        objects_result = vision_client.analyze_image(image_url, visual_features=["Objects"])
        
        # 取得所有偵測到的物件
        detected_objects = [
            # 將物件描述改為英文，以便後續翻譯
            f"Object: {obj.object_property} (Confidence: {obj.confidence:.2%})"
            for obj in objects_result.objects
        ]
        
        # 回傳結果或提示無偵測到物件
        return "； ".join(detected_objects) if detected_objects else "No objects detected" # 將多個物件描述用 "； " 連接，並將無物件提示改為英文
    
    except Exception as e:
        return "無法讀取圖片，請換一張"



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
            f"Glasses type: {face['faceAttributes'].get('glasses', 'Unknown')}, "
            f"Blur level: {face['faceAttributes'].get('blur', {}).get('blurLevel', 'Unknown')}"
            for face in faces_result
        ]

        return "； ".join(faces_detected)

    except Exception as e:
        return "無法讀取圖片，請換一張"


FUNCTION_MAP = {
    "describe": get_image_description,
    "ocr": get_image_text,
    "objects": get_detected_objects,
    "faces": get_detected_faces,
}


# Flask 處理表單
@app.route("/", methods=["GET", "POST"])
def index():
    description = ""
    image_url = ""
    selected_function = ""
    translated = ""
    ui_src_language = "en"
    dst_language = "zh-Hant"

    if request.method == "POST":
        image_url = request.form.get("image_url")
        selected_function = request.form.get("function")
        ui_src_language = request.form.get("src_language", "en")
        dst_language = request.form.get("dst_language", "zh-Hant")

        if image_url and selected_function in FUNCTION_MAP:
            # 根據選擇的功能調用相應的函數
            api_function = FUNCTION_MAP[selected_function]
            description = api_function(image_url)
            if description: # 只有在成功獲取到描述/文字時才翻譯
                translated = translate_text(description, ui_src_language, dst_language)

    return render_template("test2.html", description=description, image_url=image_url, selected_function=selected_function , translated=translated, src_language=ui_src_language, dst_language=dst_language)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)