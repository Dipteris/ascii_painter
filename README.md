# ASCII Painter

A graphical tool that converts images into ASCII character art with advanced features and intuitive controls.

## Features

- 🖼️ **Multi-format Support**: Supports PNG, JPG, JPEG, GIF, BMP, TIFF, WebP image formats
- 🎨 **Real-time Conversion**: Automatic ASCII conversion upon image selection
- 📐 **Side-by-side View**: Original image and ASCII art displayed simultaneously (1:1 aspect ratio)
- 🎯 **Interactive Controls**: Real-time sliders and spinboxes for precise adjustment
- 🔤 **Multiple ASCII Character Sets**: 7 different character sets including Unicode options
- 🔍 **Zoom Controls**: Independent zoom for both image and ASCII art viewers
- 💾 **Export Options**: Save to file or copy to clipboard
- 📊 **Real-time Histogram**: Live grayscale histogram with grid lines and value labels
- 🎛️ **Professional Image Adjustments**: Photoshop-style levels and basic adjustments
- 🚀 **Intelligent Optimization**: Automatic image downsizing for faster performance
- ⚡ **Smart Preferences**: Automatically saves and restores all your settings

## ASCII Character Sets

Choose from 7 carefully designed character sets:

1. **8-Level Minimalist (Classic)**: ` .:-=+*#%@`
2. **10-Level Coarse (Balanced)**: ` .'`^:!|#@`
3. **16-Level Alternative (Smoother)**: ` .'`^\":;Il!i~+*#%` (Default)
4. **Unicode Blocks**: ` ░▒▓█`
5. **Unicode Dot Patterns**: ` ⠀⠄⠆⠇⠿⣿`
6. **Unicode Mixed Symbols**: ` ·∘○●◉█`
7. **Unicode Shade Blocks**: ` ▁▂▃▄▅▆▇█`

## Requirements

- Python 3.8 or higher
- UV package manager (recommended) or pip

## Installation & Usage

### Using UV (Recommended)

1. **Clone and navigate to the project**:
   ```bash
   git clone https://github.com/Dipteris/ascii_painter.git
   cd ascii_painter
   ```

2. **Run directly with UV**:
   ```bash
   uv run main.py
   ```

### Alternative Method

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Run the application**:
   ```bash
   uv run main.py
   ```

## User Interface

The interface features a professional 3-section layout:

### Top Row - Professional Controls
- **Histogram**: Real-time grayscale histogram with grid lines (matches Original Image width)
- **Image Adjustments**: Photoshop-style levels and basic adjustments with individual reset buttons
- **Controls**: ASCII width, aspect ratio, mode selection, and invert colors

### Middle Row - 1:1 Viewers
- **Original Image**: Displays the selected image with zoom capability (left side)
- **ASCII Art**: Shows the converted ASCII art with font size controls (right side)

### Bottom Row - Action Controls
- **Image Controls**: Select Image, zoom In/Out/Reset for the original image
- **ASCII Controls**: Save ASCII, Copy to Clipboard, font size In/Out/Reset

## How to Use

1. **Select an Image**: Click "Select Image" to choose your image file
2. **Auto-conversion**: ASCII art generates automatically upon selection with intelligent optimization
3. **Adjust Parameters**: 
   - **Width & Aspect Ratio**: Drag sliders, use spinbox arrows, or type exact values + Enter
   - **Image Adjustments**: Fine-tune levels (Black, Gamma, White) and basic adjustments (Brightness, Contrast)
   - **ASCII Style**: Select from 7 different character sets
   - **Invert Colors**: Toggle between normal and inverted brightness mapping
4. **Monitor Histogram**: Watch real-time pixel distribution changes as you adjust settings
5. **Zoom Views**: Use controls below each viewer to zoom in/out independently
6. **Export**: Save to file or copy to clipboard when satisfied

## Technical Details

### Intelligent Image Processing
- **Smart Optimization**: Automatically downsizes large images (max 800px width) for faster performance while preserving ASCII quality
- **High-Quality Resampling**: Uses LANCZOS algorithm to maintain detail during resizing
- **Adaptive Processing**: Skips unnecessary adjustments when values are at defaults
- **Aspect Ratio Control**: User-adjustable aspect ratio with 100% = no distortion, 55% = character compensation

### Professional Image Adjustments
- **Levels Control**: Black level (0-255), Gamma (0.1-3.0), White level (0-255)
- **Basic Adjustments**: Brightness (-100 to +100), Contrast (-100 to +100)
- **Real-time Histogram**: Live pixel distribution visualization with grid lines
- **Invert Colors**: Toggle between normal and inverted brightness mapping

### Conversion Algorithm
- Maintains aspect ratio during resizing
- Converts to grayscale for optimal character mapping
- Maps pixel brightness to character density
- Applies user-adjustable character height compensation

### Advanced Features
- **Real-time Everything**: Instant feedback on all parameter changes with live histogram updates
- **Multiple Input Methods**: Sliders, spinboxes with up/down arrows, and direct text entry
- **Preference Persistence**: All settings saved in `ascii_painter_config.json`
- **Unicode Support**: Modern character sets for enhanced visual quality
- **Responsive Interface**: Professional layout with 1:1 viewer ratio and adaptive histogram sizing

## Project Structure

```
ascii_painter/
├── main.py                    # Main application file
├── pyproject.toml            # UV project configuration
├── uv.lock                   # Dependency lock file
├── ascii_painter_config.json # User preferences (auto-generated)
└── README.md                 # This file
```

## Configuration

The application automatically saves all your preferences:
- ASCII character set selection
- Image adjustments (levels, brightness, contrast)
- Aspect ratio and invert colors settings
- Font size for ASCII display
- All settings persist between sessions and are stored in `ascii_painter_config.json`

## System Compatibility

- **macOS**: Full support with native UI elements
- **Windows**: Compatible with all features
- **Linux**: Full functionality with tkinter support

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**ASCII Painter** - Transform your images into unique text art with professional-grade image adjustments, real-time histogram visualization, and lightning-fast performance optimization!