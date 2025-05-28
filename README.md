# ASCII 畫家

一款將圖片轉換為 ASCII 字符藝術的圖形化工具程式。

## 功能特色

- 🖼️ **圖片選擇**：支援多種常見圖片格式（PNG、JPG、JPEG、GIF、BMP、TIFF、WebP）
- 🎨 **即時轉換**：將圖片轉換為精美的 ASCII 字符藝術
- 📐 **比較檢視**：左側顯示原始圖片，右側顯示 ASCII 藝術作品
- ⚙️ **可調參數**：自訂 ASCII 輸出寬度（20-200 字符）
- 💾 **多種輸出**：支援儲存至檔案或複製到剪貼簿
- 🎯 **使用者友善**：直觀的圖形化介面

## 系統需求

- Python 3.7 或更新版本
- Pillow 函式庫

## 安裝說明

1. **建立並啟用虛擬環境**：
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **安裝相依套件**：
   ```bash
   pip install -r requirements.txt
   ```

3. **執行程式**：
   ```bash
   python ascii_painter.py
   ```

## 使用方法

1. 點擊「選擇圖片」按鈕來選擇您想要轉換的圖片
2. 根據需要調整 ASCII 寬度設定（預設為 80 字符）
3. 點擊「轉換為 ASCII」按鈕開始轉換
4. 在左側檢視原始圖片，右側檢視 ASCII 藝術作品
5. 使用「儲存 ASCII」將結果儲存為文字檔案
6. 使用「複製到剪貼簿」將 ASCII 藝術複製到剪貼簿

## 技術細節

### ASCII 字符集
程式使用密度漸變的字符集：` .:-=+*#%@`（從淺到深）

### 轉換演算法
- 根據指定寬度調整圖片大小
- 自動維持長寬比例
- 轉換為灰階圖片
- 將像素亮度對應到 ASCII 字符

### 支援的圖片格式
- PNG（.png）
- JPEG（.jpg, .jpeg）
- GIF（.gif）
- BMP（.bmp）
- TIFF（.tiff）
- WebP（.webp）

## 專案結構

```
ascii_painter/
├── ascii_painter.py    # 主程式檔案
├── requirements.txt    # Python 相依套件
└── README.md          # 說明文件
```

## 授權條款

此專案採用 MIT 授權條款。

## 貢獻指南

歡迎提交 Issue 和 Pull Request 來改善這個專案！

---

**ASCII 畫家** - 讓您的圖片變身為獨特的文字藝術作品！