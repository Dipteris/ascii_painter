# ASCII Painter 🎨

Transform your photos into stunning ASCII art with professional-grade image controls and real-time preview!

## ✨ What is ASCII Painter?

ASCII Painter is a powerful desktop application that converts your images into beautiful text art. Whether you want to create retro-style artwork, add a unique touch to your projects, or just have fun with your photos, ASCII Painter provides professional-grade tools that make it simple and enjoyable.

**Key Features:**
- 🎛️ **Professional Image Controls** - Levels, gamma, brightness, contrast adjustments
- 📊 **Real-time Histogram** - See exactly how your adjustments affect the image
- 🎨 **7 Character Styles** - From classic ASCII to modern Unicode blocks
- 🖌️ **ASCII Paintbrush** - Paint directly on ASCII art with character-based drawing tools
- ⚡ **Instant Preview** - All changes update live as you adjust settings
- 💾 **Smart Export** - Save as text files or copy directly to clipboard
- 🔄 **Memory** - All preferences automatically saved between sessions

## 🚀 Quick Start

### One-Click Launch (Recommended)
```bash
git clone https://github.com/yourusername/ascii_painter.git
cd ascii_painter
uv run main.py
```

### Alternative: Install Dependencies First
```bash
git clone https://github.com/yourusername/ascii_painter.git
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

### Step 4: Paint Your Art (NEW!)
- **Enable Paintbrush**: Check the "Enable Paintbrush" box in the ASCII Paintbrush panel
- **Choose Character**: Select any character from your current ASCII character set
- **Set Brush Size**: Adjust size (1-5) for precise or broad strokes
- **Click & Drag**: Paint directly on the ASCII art with your mouse
- **Reset**: Use "Reset ASCII" to return to the original conversion

### Step 5: Save Your Creation
- **Save to File**: Export as a text file to share or use later (includes paintbrush edits)
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
| **Dense** | ` .,-~:;!*+<%@#` | High detail and contrast |

## 🎛️ Professional Controls

### Advanced Image Adjustments
- **Levels Control**: Black level (0-254) and white level (1-255) for precise tonal control
- **Gamma Correction**: 0.1-3.0 range with 0.01 precision for midtone adjustments
- **Brightness & Contrast**: -100 to +100 range for fine-tuning
- **Real-time Histogram**: 64-bin histogram with live updates and grid overlay
- **Invert Colors**: Toggle for negative effects and artistic styles

### Smart Features & Performance
- **Auto-Optimization**: Large images intelligently downscaled (max 1200px height)
- **EXIF Orientation**: Automatic rotation correction for photos from cameras
- **Memory System**: All 10+ settings automatically saved to config file
- **Dual Zoom Controls**: Independent zoom for original image (0.1x-5.0x) and ASCII text (4-24px)
- **Multiple Input Methods**: Sliders, direct number input, and increment/decrement buttons
- **Debounced Updates**: Smooth performance during rapid adjustments

## 🖥️ Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│  📊 Histogram    🎛️ Adjustments     ⚙️ Controls       │
├─────────────────────────────────────────────────────────┤
│  🖼️ Original Image     📝 ASCII Art   🖌️ Paintbrush    │
├─────────────────────────────────────────────────────────┤
│  🔧 Image Controls              💾 Export Controls      │
└─────────────────────────────────────────────────────────┘
```

### ASCII Paintbrush Panel (NEW!)
Located to the right of the ASCII Art viewer:
- **Enable Paintbrush**: Toggle painting mode on/off
- **Brush Size**: Square brush patterns from 1x1 to 5x5 characters
- **Brush Character**: Choose from current ASCII character set (updates automatically when you change styles)
- **Reset ASCII**: Restore original ASCII art, removing all paint modifications

## 💡 Tips for Best Results

### ASCII Conversion
- **Start Simple**: Begin with the default settings and adjust from there
- **Try Different Styles**: Each character set creates a unique artistic effect
- **Use Contrast**: High-contrast images often produce the most striking ASCII art
- **Experiment with Size**: Larger width values capture more detail
- **Check the Histogram**: A good spread across the histogram usually means better ASCII art

### ASCII Paintbrush
- **Character Selection**: Darker characters (like `#`, `@`, `█`) work well for shadows and emphasis
- **Brush Size**: Use size 1 for fine details, larger sizes for filling areas
- **Style Matching**: Choose brush characters that complement your ASCII character set
- **Save Frequently**: Your paintbrush edits are included in saves/copies but reset when reconverting

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

**Paintbrush not working?**
- Make sure "Enable Paintbrush" is checked
- Ensure you have ASCII art displayed (load an image first)
- Try clicking and dragging on the ASCII text area
- Check that you've selected a brush character

## ⚙️ Technical Details

### Architecture
- **Single-file Application**: All functionality in one well-organized Python file (`main.py`)
- **Dependencies**: PIL/Pillow (≥10.0.0) and NumPy (≥1.21.0) for high-performance image processing
- **GUI Framework**: tkinter (built-in) for cross-platform desktop compatibility
- **Configuration**: JSON-based settings with automatic persistence

### Performance Optimizations
- **Smart Image Downscaling**: Large images automatically optimized for processing speed
- **Vectorized Operations**: NumPy arrays for efficient brightness mapping and adjustments
- **Memory Management**: Efficient PIL image handling with proper resource cleanup
- **Debounced UI Updates**: Prevents excessive recomputation during rapid slider adjustments

### Image Processing Pipeline
1. **Load & Orientation**: PIL with automatic EXIF orientation correction
2. **Optimization**: Intelligent downscaling for performance (max 1200px height)
3. **Adjustments**: Levels → Gamma → Brightness → Contrast → Inversion
4. **ASCII Conversion**: Character mapping with height compensation (0.55 factor)
5. **Display**: Real-time preview with zoom and scroll capabilities

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