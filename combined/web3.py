import os
from flask import Flask, render_template, request, url_for
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
import requests
import time

app = Flask(__name__) #建立一個 Flask app 實例

# 載入 .env
load_dotenv()

# Azure 服務金鑰與端點設定
# 電腦視覺 
VISION_KEY = os.getenv("VISION_KEY")
VISION_ENDPOINT = os.getenv("VISION_ENDPOINT")

# 翻譯 
KEY = os.getenv("KEY")
REGION = os.getenv("REGION")
ENDPOINT = os.getenv("ENDPOINT")

# 語音合成 
TTS_KEY = os.getenv("TTS_KEY")
TTS_REGION = os.getenv("TTS_REGION")


# 用於調用 電腦視覺 API
# 初始化 Computer Vision Client
vision_client = ComputerVisionClient(
    VISION_ENDPOINT, CognitiveServicesCredentials(VISION_KEY)
)

# 用於調用 翻譯 API
translator_client = TextTranslationClient(
    endpoint=ENDPOINT,
    credential=TranslatorCredential(KEY, REGION)
)

# 將輸入的文字 text_to_speak，用 Azure 的語音合成（TTS）轉換成語音檔
def azure_text_to_speech(text_to_speak, target_lang_code_from_form):
    """
    Generates speech from text using Azure TTS.
    target_lang_code_from_form: Language code like "en", "zh-Hant", "ja", etc.
    """
    # 確認語音合成服務的金鑰與區域是否存在
    if not TTS_KEY or not TTS_REGION:
        print("Error: TTS_KEY or TTS_REGION environment variables not set.")
        return None
    # 如果輸入的文字是空的，無法合成，直接返回 None
    if not text_to_speak:
        print("Error: Text to speak is empty.")
        return None

    # 根據區域組合出 Azure TTS 服務的 API endpoint
    endpoint = f"https://{TTS_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": TTS_KEY,# 認證的金鑰
        "Content-Type": "application/ssml+xml", # SSML（語音合成標記語言）格式
        "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",# 指定輸出音訊格式為 16kHz、32kbps、單聲道 mp3
        "User-Agent": "python-requests" # 用於標示請求端
    }
    # SSML:Speech Synthesis Markup Language（語音合成標記語言)，用來控制文字轉語音（TTS）時的語音合成效果。
    # 根據使用者傳入的語言代碼，對應 Azure SSML 所需的語言標籤與聲音名稱
    lang_voice_map = {
        "en": ("en-US", "en-US-JennyNeural"),
        "zh-Hans": ("zh-CN", "zh-CN-XiaoxiaoNeural"),
        "zh-Hant": ("zh-TW", "zh-TW-HsiaoChenNeural"),
        "ja": ("ja-JP", "ja-JP-NanamiNeural"),
        "ko": ("ko-KR", "ko-KR-SunHiNeural"),
    }
    # 如果找不到匹配，使用英文語音作為預設
    default_ssml_lang = "en-US" 
    default_ssml_voice = "en-US-JennyNeural"

    ssml_lang, ssml_voice_name = lang_voice_map.get(target_lang_code_from_form, (default_ssml_lang, default_ssml_voice))

    # 使用 SSML 格式來描述語音合成的內容
    ssml = f"""
    <speak version='1.0' xml:lang='{ssml_lang}'>
        <voice xml:lang='{ssml_lang}' name='{ssml_voice_name}'>
            {text_to_speak}
        </voice>
    </speak>
    """

    # 發送 HTTP POST 請求並處理回應
    try:
        response = requests.post(endpoint, headers=headers, data=ssml.encode("utf-8"))
        response.raise_for_status() # Will raise an HTTPError for bad status codes
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Speech synthesis API error: {e}")
        return None







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
    audio_url = None # Initialize audio_url

    if request.method == "POST":
        image_url = request.form.get("image_url")
        selected_function = request.form.get("function")
        ui_src_language = request.form.get("src_language", ui_src_language)
        dst_language = request.form.get("dst_language", dst_language)

        # Determine the source language for translation. If "無" (empty string) is selected,
        # Azure Translator will attempt auto-detection.
        actual_src_language_for_translation = ui_src_language if ui_src_language else None

        if image_url and selected_function in FUNCTION_MAP:
            # 根據選擇的功能調用相應的函數
            api_function = FUNCTION_MAP[selected_function]
            description = api_function(image_url)

            # Check for critical processing errors from vision functions
            critical_error_messages = [
                "無法讀取圖片，請換一張",

            ]
            is_critical_error = any(msg in description for msg in critical_error_messages if description)

            if description and not is_critical_error:
                translated = translate_text(description, actual_src_language_for_translation, dst_language)
                
                if translated and not translated.startswith("翻譯時發生錯誤："):
                    # Generate speech for the translated text
                    audio_data = azure_text_to_speech(translated, dst_language)
                    if audio_data:
                        static_dir = os.path.join(app.root_path, 'static')
                        os.makedirs(static_dir, exist_ok=True) # Ensure static directory exists
                        
                        audio_filename = "translated_speech.mp3"
                        audio_file_path = os.path.join(static_dir, audio_filename)
                        try:
                            with open(audio_file_path, "wb") as f:
                                f.write(audio_data)
                            audio_url = url_for('static', filename=audio_filename, v=int(time.time()))
                        except IOError as e:
                            print(f"Error writing audio file: {e}")
                            # audio_url remains None or its previous value
            elif not description or is_critical_error: # If description is empty or a critical error occurred
                translated = "" # No translation if vision part failed critically

    return render_template("test3.html", description=description, image_url=image_url, selected_function=selected_function , translated=translated, src_language=ui_src_language, dst_language=dst_language, audio_url=audio_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)