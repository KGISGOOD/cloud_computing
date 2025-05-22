# Cloud Computing Final Project

## 📘 專案簡介
本專案的核心目標，是建立一種能跨越語言與感官障礙的資訊傳遞方式，讓圖片不再只是視覺資訊的載體，而能被更多使用者理解、聆聽與互動，對於視障者、外語使用者或閱讀不便者而言，能幫助他們理解圖片中的文字內容。使用者可先上傳圖片網址，由系統自動辨識圖片，接著選取所需功能，並提供四種語言翻譯的選項，最後再透過語音合成的方式，將文字內容以語音播放。

# ☁️ Azure AI 專案部署說明文件

本文件詳細紀錄從 Azure 資源建立、Docker 容器建構、映像上傳到 ACR，再到容器實際執行的完整過程，適用於部署 AI 模型應用程式至雲端環境。

---

## 📁 1. 建立資源群組

建立資源群組 `[群組名稱]`，用於集中管理所有 AI 相關服務。

---

## 🤖 2. 建立 AI 服務

建立以下 AI 服務，並**確保定價層為 Free F0**：

- 🔍 圖像辨識（Computer Vision）
- 🌐 翻譯（Translator）
- 🗣️ 文字轉語音（Text-to-Speech）

---

## 🔑 3. 取得端點與金鑰

前往每個服務的 **金鑰與端點** 頁面，複製內容供程式使用。

📷 *範例圖：*

![端點與金鑰位置](combined/img/1.png)


---

## 🐳 4. 建構 Docker 映像檔

在專案根目錄執行以下指令：

```bash
docker image build -t final:latest .
```

---

## 🖥️ 5. 執行本地容器

```bash
docker container run -d --name final -p 8080:8080 final:latest
```

可透過 `http://localhost:8080` 驗證是否執行成功。

---

## 📦 6. 創建一個資源群組

創建一個資源群組 final_project (用來存放我們的最終成果)

---

## 🏗️ 7. 創建 Azure Container Registry

於 Azure Portal 中創建 ACR（建議使用標準命名格式）

📷 *範例圖：*


![建構映像檔畫面](combined/img/002.png)

---

## 🔐 8. 啟用 Azure Container Registry 的管理使用者，取得金鑰

📷 *範例圖：*

![取得 ACR 金鑰](combined/img/003.png)

---

## 🔑 9. 登入 Azure Container Registry

```bash
docker login finalpodcast.azurecr.io
```

輸入以下帳密：

- Username: `finalpodcast`
- Password: `[password or password2]`

成功會顯示：

```bash
Login Succeeded
```

---

## 🛠️ 10. 建立自定義的映像檔

```bash
docker image build -t finalpodcast.azurecr.io/finalpodcast:latest .
```

---

## ☁️ 11. 將Docker映像檔上傳到 Azure Container Registry

```bash
docker image push finalpodcast.azurecr.io/finalpodcast:latest
```

---

## 🚀 12. 建立容器執行個體並使用 IP 存取

在 Azure Portal 建立容器執行個體（Container Instance），**指定公開連接埠為 8080**。

執行後請使用以下格式存取：

```
http://[公用 IP 位址]:8080
```

📷 *範例圖：*

![建立容器執行個體](combined/img/004.png)

---

## ✅ 結語

你已成功將專案部署至 Azure 平台，恭喜恭喜🎊
















## 💡 功能介紹


## 🧾 程式碼說明
- `web3.py`：主要邏輯
- `requirements.txt`：依賴列表

## 📸 成果展示


## 📎 附件
- 圖片url