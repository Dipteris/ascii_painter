# ASCII Painter

A graphical tool that converts images into ASCII character art with advanced features and intuitive controls.

## Features

- 🖼️ **Multi-format Support**: Supports PNG, JPG, JPEG, GIF, BMP, TIFF, WebP image formats
- 🎨 **Real-time Conversion**: Automatic ASCII conversion upon image selection
- 📐 **Side-by-side View**: Original image and ASCII art displayed simultaneously
- 🎯 **Interactive Width Control**: Real-time slider and spinbox for precise width adjustment (20-200 characters)
- 🔤 **Multiple ASCII Character Sets**: 7 different character sets including Unicode options
- 🔍 **Zoom Controls**: Independent zoom for both image and ASCII art viewers
- 💾 **Export Options**: Save to file or copy to clipboard
- 🎛️ **Organized Interface**: Logical grouping of controls for optimal workflow
- ⚡ **Smart Preferences**: Automatically saves and restores your settings

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
   git clone <repository-url>
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

The interface is organized into logical groups:

### Control Panels (Top Row)
- **File Operations**: Select Image, Save ASCII, Copy to Clipboard
- **ASCII Controls**: Width slider/spinbox, ASCII mode selection

### Viewer Panels (Middle Row)
- **Original Image**: Displays the selected image with zoom capability
- **ASCII Art**: Shows the converted ASCII art with font size controls

### Viewer Controls (Bottom Row)
- **Image Controls**: Zoom In/Out/Reset for the original image
- **ASCII Controls**: Font size In/Out/Reset for the ASCII display

## How to Use

1. **Select an Image**: Click "Select Image" to choose your image file
2. **Auto-conversion**: ASCII art generates automatically upon selection
3. **Adjust Width**: 
   - Drag the slider for real-time preview
   - Use spinbox arrows for step-by-step adjustment
   - Type exact values and press Enter
4. **Choose ASCII Style**: Select from 7 different character sets
5. **Zoom Views**: Use controls below each viewer to zoom in/out
6. **Export**: Save to file or copy to clipboard when satisfied

## Technical Details

### Conversion Algorithm
- Maintains aspect ratio during resizing
- Converts to grayscale for optimal character mapping
- Maps pixel brightness to character density
- Applies character height compensation (0.55 factor)

### Advanced Features
- **Real-time Conversion**: Instant feedback on all parameter changes
- **Debounced Input**: Smooth interaction without performance issues
- **Preference Persistence**: Settings saved in `ascii_painter_config.json`
- **Unicode Support**: Modern character sets for enhanced visual quality
- **Responsive UI**: Layout adapts to content without disrupting controls

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

The application automatically saves your preferences:
- Selected ASCII character set
- Font size for ASCII display
- All settings persist between sessions

## System Compatibility

- **macOS**: Full support with native UI elements
- **Windows**: Compatible with all features
- **Linux**: Full functionality with tkinter support

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**ASCII Painter** - Transform your images into unique text art with professional-grade controls and real-time feedback!