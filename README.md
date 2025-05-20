# 專案設定與執行

本指南將引導您如何設定 Python 虛擬環境、安裝必要的依賴套件，以及執行 `main.py` 腳本。

## 事前準備

在開始之前，請確保您的系統已安裝 Python 3.13。

## 安裝與設定

請依照以下步驟來啟動並運行您的專案：

1.  **建立虛擬環境：**
    強烈建議使用虛擬環境來管理專案的依賴套件。此指令將在您的專案目錄中建立一個名為 `venv` 的新虛擬環境。

    ```bash
    python3.13 -m venv venv
    ```

2.  **啟用虛擬環境：**
    在安裝依賴套件之前，您需要啟用虛擬環境。

    * **在 macOS/Linux 上：**

        ```bash
        source venv/bin/activate
        ```

    * **在 Windows (命令提示字元) 上：**

        ```bash
        venv\Scripts\activate.bat
        ```

    * **在 Windows (PowerShell) 上：**

        ```bash
        venv\Scripts\Activate.ps1
        ```

3.  **安裝依賴套件：**
    虛擬環境啟用後，使用 pip 安裝所需的函式庫。

    ```bash
    pip install requests playsound==1.2.2
    ```

## 執行專案

完成設定後，您可以執行您的主腳本：

```bash
python main.py
```

## 停用虛擬環境
當您完成專案工作後，可以停用虛擬環境：

```bash
deactivate
```


    