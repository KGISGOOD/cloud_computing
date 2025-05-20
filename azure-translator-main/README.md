# azure-translator
Azure AI 翻譯工具測試範例([參考文件](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-translation-text-readme?view=azure-python-preview))

# 測試環境設定
1. [建議] 先建立虛擬環境
2. 在虛擬環境中安裝需要的套件

   `pip install -r requirements.txt`

# 修改環境變數
將 Azure AI 翻譯工具對應的區域、金鑰、服務端點寫入環境變數檔案(`.env`)

# 測試單機應用程式(app.py)
1. 依據需要修改 app.py (例如，來源語言、目標語言、待翻譯文字)
2. 執行 app.py

   `python app.py`

# 測試 API 服務(api.py)
1. 執行 api.py

   `python api.py`
2. 開啟瀏覽器並前往 [http://127.0.0.1:8080/?src=en&dst=zh-Hant&text=Hello World](http://127.0.0.1:8080/?src=en&dst=zh-Hant&text=Hello%20World)

# 測試網頁頁用程式(web.py)
1. 執行 web.py

   `python web.py`
2. 開啟瀏覽器並前往 http://127.0.0.1:8080

# 練習
1. 將 web.py 部署到 Azure Virtual Machine。
2. 將 web.py 部署到 Azure Contrainer Instance。
3. 將 api.py 部署到 Azure Function 。