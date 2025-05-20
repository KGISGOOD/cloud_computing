import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.ai.translation.text import TextTranslationClient
from azure.ai.translation.text.models import InputTextItem

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

# 初始化 Translator Client
translator_client = TextTranslationClient(
    endpoint=ENDPOINT,
    credential=KEY,
    region=REGION
)

def get_image_description(image_url):
    try:
        description_result = vision_client.describe_image(image_url)
        if description_result.captions:
            return description_result.captions[0].text
        return ""
    except Exception as e:
        return f"取得描述時發生錯誤：{e}"

def translate_text(text, src_language, dst_language):
    try:
        targets = [InputTextItem(text=text)]
        responses = translator_client.translate(
            body=targets, 
            to=[dst_language],
            from_parameter=src_language
        )
        return responses[0].translations[0].text
    except Exception as e:
        return f"翻譯時發生錯誤：{e}"
    
    
@app.route("/", methods=["GET", "POST"])
def index():
    description = ""
    translated = ""
    image_url = ""
    src_language = "en"
    dst_language = "zh-Hant"
    if request.method == "POST":
        image_url = request.form.get("image_url")
        src_language = request.form.get("src_language", "en")
        dst_language = request.form.get("dst_language", "zh-Hant")
        if image_url:
            description = get_image_description(image_url)
            if description and not description.startswith("取得描述時發生錯誤"):
                translated = translate_text(description, src_language, dst_language)
            else:
                translated = ""
    return render_template(
        "index.html",
        description=description,
        translated=translated,
        image_url=image_url,
        src_language=src_language,
        dst_language=dst_language
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)