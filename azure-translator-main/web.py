"""
    Azure AI 翻譯工具(網頁版)
"""
import os
import pathlib
from dotenv import load_dotenv
from flask import Flask, request, render_template
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem

# 如果.env存在，讀取.env檔案
env_path = pathlib.Path(".env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

# 取得環境變數
REGION = os.getenv('REGION')
KEY = os.getenv('KEY')
ENDPOINT = os.getenv('ENDPOINT')

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def translator():
    """
        Azure AI 翻譯工具(網頁版)
    """
    src_language = "en"
    dst_language = "zh-Hant"
    input_text = ""
    translated_text = ""

    if request.method == 'POST':
        src_language = request.form.get("src_language")
        input_text = request.form.get("input_text")
        dst_language = request.form.get("dst_language")

        client = TextTranslationClient(
            endpoint=ENDPOINT,
            credential=TranslatorCredential(KEY, REGION)
        )

        src = src_language # 來源語言
        dst = [dst_language] # 目標語言(可多個)
        targets = [InputTextItem(text=input_text)] # 目標文字(可多個)
        responses = client.translate(content=targets, to=dst, from_parameter=src)
        translation = responses[0].translations[0]
        translated_text=translation.text

    return render_template("index.html",
                           src_language=src_language,
                           input_text=input_text,
                           dst_language=dst_language,
                           translated_text=translated_text)

if __name__ == '__main__':
    print(REGION, KEY, ENDPOINT)
    app.run(host='0.0.0.0', port=8080)
