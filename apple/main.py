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

# 主程式邏輯
# 這個 if __name__ == "__main__": 區塊是程式的進入點
if __name__ == "__main__":
    text = input("請輸入要轉語音的文字：")
    try:
        audio_data = azure_text_to_speech(text)

        # 將音訊資料儲存為 mp3 檔
        with open("output.mp3", "wb") as f:
            f.write(audio_data)
        print("✅ 語音合成成功，已儲存為 output.mp3")

        # 播放音訊
        print("▶️ 開始播放語音...")
        playsound("output.mp3")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
