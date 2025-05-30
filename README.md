# ASCII Painter 🎨

Transform your photos into stunning ASCII art with professional-grade image controls and real-time preview!

![ASCII Painter Screenshot](https://via.placeholder.com/800x600/f0f0f0/333333?text=ASCII+Painter+Screenshot)

## ✨ What is ASCII Painter?

ASCII Painter is an easy-to-use desktop application that converts your images into beautiful text art. Whether you want to create retro-style artwork, add a unique touch to your projects, or just have fun with your photos, ASCII Painter makes it simple and enjoyable.

## 🚀 Quick Start

### Option 1: One-Click Launch (Recommended)
```bash
git clone https://github.com/Dipteris/ascii_painter.git
cd ascii_painter
uv run main.py
```

### Option 2: Install and Run
```bash
git clone https://github.com/Dipteris/ascii_painter.git
cd ascii_painter
uv sync
uv run main.py
```

**Requirements**: Python 3.8+ and [UV package manager](https://docs.astral.sh/uv/getting-started/installation/)

## 🎯 How to Use

### Step 1: Load Your Image
Click **"Select Image"** and choose any photo from your computer. ASCII Painter supports all common formats: PNG, JPG, GIF, BMP, TIFF, and WebP.

### Step 2: Customize Your Art
- **Choose Style**: Pick from 7 different ASCII character sets (classic symbols to modern Unicode)
- **Adjust Size**: Use the width slider to make your art bigger or smaller
- **Fine-tune Look**: Adjust brightness, contrast, and other image settings
- **Perfect Proportions**: Use the aspect ratio control to get the perfect shape

### Step 3: Watch the Magic
Your ASCII art updates instantly as you make changes! The live histogram shows you how your adjustments affect the image.

### Step 4: Save Your Creation
- **Save to File**: Export as a text file to share or use later
- **Copy to Clipboard**: Paste directly into documents, social media, or anywhere you want

## 🎨 Character Styles

Choose the perfect style for your art:

| Style | Characters | Best For |
|-------|------------|----------|
| **Classic** | ` .:-=+*#%@` | Traditional ASCII art |
| **Smooth** | ` .'`^\":;Il!i~+*#%` | Detailed images (Default) |
| **Blocks** | ` ░▒▓█` | Bold, modern look |
| **Dots** | ` ⠀⠄⠆⠇⠿⣿` | Unique dotted effect |
| **Symbols** | ` ·∘○●◉█` | Artistic circles |
| **Shade Blocks** | ` ▁▂▃▄▅▆▇█` | Gradient effects |

## 🎛️ Professional Controls

### Image Adjustments
- **Brightness & Contrast**: Make your image pop
- **Levels Control**: Fine-tune shadows, midtones, and highlights like Photoshop
- **Real-time Histogram**: See exactly how your changes affect the image
- **Invert Colors**: Flip black and white for different effects

### Smart Features
- **Auto-Optimization**: Large images are automatically resized for faster processing
- **Memory**: All your settings are remembered between sessions
- **Zoom**: Independently zoom your original image and ASCII art
- **Multiple Input**: Use sliders, type exact numbers, or use arrow buttons

## 🖥️ Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│  📊 Histogram    🎛️ Adjustments     ⚙️ Controls       │
├─────────────────────────────────────────────────────────┤
│  🖼️ Original Image              📝 ASCII Art          │
├─────────────────────────────────────────────────────────┤
│  🔧 Image Controls              💾 Export Controls      │
└─────────────────────────────────────────────────────────┘
```

## 💡 Tips for Best Results

- **Start Simple**: Begin with the default settings and adjust from there
- **Try Different Styles**: Each character set creates a unique artistic effect
- **Use Contrast**: High-contrast images often produce the most striking ASCII art
- **Experiment with Size**: Larger width values capture more detail
- **Check the Histogram**: A good spread across the histogram usually means better ASCII art

## 🔧 Troubleshooting

**App won't start?**
- Make sure you have Python 3.8+ installed
- Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`

**Image looks wrong?**
- Try adjusting the aspect ratio slider
- Use the "Reset All" button to start over
- Check if "Invert Colors" should be toggled

**ASCII art too small/large?**
- Use the width slider to adjust size
- Use font zoom controls (In/Out/Reset) to change text size

## 🌟 What Makes ASCII Painter Special

- **Real-time Preview**: See changes instantly as you adjust settings
- **Professional Quality**: Advanced image processing algorithms for the best results
- **User-Friendly**: No technical knowledge required - just point, click, and create
- **Lightning Fast**: Optimized for performance even with large images
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📁 Your Files

ASCII Painter creates these files:
- `ascii_painter_config.json` - Saves your preferences (you can delete this to reset)
- Your exported ASCII art files (wherever you choose to save them)

## 🤝 Get Help & Contribute

- **Questions?** Open an issue on [GitHub](https://github.com/Dipteris/ascii_painter/issues)
- **Ideas?** We'd love to hear your suggestions!
- **Want to Help?** Contributions are always welcome

## 📄 License

MIT License - Use it however you want!

---

**Ready to create amazing ASCII art?** [Download ASCII Painter](https://github.com/Dipteris/ascii_painter) and start transforming your images today! 🚀