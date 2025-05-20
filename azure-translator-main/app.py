"""
    Azure AI 翻譯工具(單機版)
"""
import os
import pathlib
from dotenv import load_dotenv
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

# Azure 翻譯工具參數
# 來源語言
SRC = "en"
# 目標語言(可多個)
DST = ["zh-hant","ja"]
# 待翻譯文字(可多個)
TARGETS =  ["Cloud computing service is fun.", "Welcome to Soochow University"]

text_translator = TextTranslationClient(
    endpoint=ENDPOINT,
    credential=TranslatorCredential(KEY, REGION)
)

TEXTS = []
for target in TARGETS:
    TEXTS.append(InputTextItem(text=target))

responses = text_translator.translate(content=TEXTS, to=DST, from_parameter=SRC)

for response in responses:
    print(response)
