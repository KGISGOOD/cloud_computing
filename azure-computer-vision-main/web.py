"""
    Azure AI 電腦視覺(網頁版)
"""
import os
import pathlib
from dotenv import load_dotenv
from flask import Flask, request, render_template
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

# 如果.env存在，讀取.env檔案
env_path = pathlib.Path(".env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

# 取得環境變數
KEY = os.getenv('KEY')
ENDPOINT = os.getenv('ENDPOINT')

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def object_detection():
    """
        Azure AI 電腦視覺(網頁版)
    """
    image_url  = ""
    language = "en"
    description = ""

    if request.method == 'POST':
        image_url = request.form.get("image_url")

        print(image_url)

        client = ComputerVisionClient(
            endpoint=ENDPOINT,
            credentials=CognitiveServicesCredentials(KEY)
        )

        analysis = client.describe_image(url=image_url, max_descriptions=1, language=language)
        result = analysis.captions[0]
        description = f"{result.text} [{result.confidence}]"
        print(description)

    return render_template("index.html",
                           image_url=image_url,
                           description=description)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
