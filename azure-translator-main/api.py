"""
    Azure AI 翻譯工具(API 版)
"""
import os
import pathlib
from dotenv import load_dotenv
from flask import Flask, request
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
        src: 來源語言
        text: 目標文字
        dst: 目標語言
    """
    src = request.args.get('src')
    text = request.args.get('text')
    dst = request.args.get('dst')

    if src and text and dst:
        client = TextTranslationClient(
            endpoint=ENDPOINT,
            credential=TranslatorCredential(KEY, REGION)
        )

        dst = [dst]
        text = [InputTextItem(text=text)] # 目標文字(可多個)
        responses = client.translate(content=text, to=dst, from_parameter=src)
        translation = responses[0].translations[0]
        translated_text=translation.text

        return translated_text

    return "Please provide src, text, and dst parameters."

if __name__ == '__main__':
    print(REGION, KEY, ENDPOINT)
    app.run(host='0.0.0.0', port=8080)
