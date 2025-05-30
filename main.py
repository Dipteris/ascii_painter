#!/usr/bin/env python3
"""
ASCII Painter - Convert images to ASCII art with GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageOps
import io
import os
import tempfile
import json
import numpy as np

class ASCIIPainter:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII Painter")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # ASCII character sets
        self.ascii_sets = {
            "8-Level Minimalist (Classic)": " .:-=+*#%@",
            "10-Level Coarse (Balanced)": " .'`^:!|#@",
            "16-Level Alternative (Smoother)": " .'`^\":;Il!i~+*#%",
            "Unicode Blocks": " ░▒▓█",
            "Unicode Dot Patterns": " ⠀⠄⠆⠇⠿⣿",
            "Unicode Mixed Symbols": " ·∘○●◉█",
            "Unicode Shade Blocks": " ▁▂▃▄▅▆▇█"
        }
        
        # Current settings
        self.current_ascii_set = "16-Level Alternative (Smoother)"
        self.ascii_chars = self.ascii_sets[self.current_ascii_set]
        self.invert_colors = False
        self.aspect_ratio = 100  # Default 100% (no distortion)
        
        # Image adjustment settings
        self.black_level = 0      # 0-255
        self.white_level = 255    # 0-255  
        self.gamma = 1.0          # 0.1-3.0
        self.brightness = 0       # -100 to +100
        self.contrast = 0         # -100 to +100
        
        # Current image data
        self.original_image = None
        self.ascii_text = ""
        
        # Zoom settings
        self.image_zoom = 1.0
        self.ascii_font_size = 8
        
        
        # Load preferences
        self.load_preferences()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights - 3 columns: 1:1.5:1.5
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)  # Wider for histogram
        main_frame.columnconfigure(2, weight=2)  # Wider for adjustments
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="ASCII Painter", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        # === TOP ROW - 3 SECTIONS ===
        
        # Section 1: Histogram (matches Original Image width - spans columns 0-1)
        histogram_frame = ttk.LabelFrame(main_frame, text="Histogram", padding="5")
        histogram_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 2), pady=(0, 10))
        histogram_frame.columnconfigure(0, weight=1)
        histogram_frame.rowconfigure(0, weight=1)
        
        # Create responsive canvas for histogram
        self.hist_canvas = tk.Canvas(histogram_frame, bg='white', relief=tk.SUNKEN, borderwidth=1)
        self.hist_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bind resize event to update histogram when container changes
        self.hist_canvas.bind('<Configure>', self.on_histogram_resize)
        
        # Initialize empty histogram
        self.update_histogram(None)
        
        # Section 2: Image Adjustments (left part of ASCII viewer width - column 2)
        adjustments_frame = ttk.LabelFrame(main_frame, text="Image Adjustments", padding="5")
        adjustments_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2, 2), pady=(0, 10))
        
        # Levels Section
        levels_label = ttk.Label(adjustments_frame, text="Levels", font=('Arial', 9, 'bold'))
        levels_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Black Level
        ttk.Label(adjustments_frame, text="Black:").grid(row=1, column=0, sticky=tk.W)
        
        black_frame = ttk.Frame(adjustments_frame)
        black_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        black_frame.columnconfigure(0, weight=1)
        
        self.black_var = tk.IntVar(value=self.black_level)
        black_slider = tk.Scale(black_frame, from_=0, to=255, variable=self.black_var, 
                               orient=tk.HORIZONTAL, command=self.on_black_change, 
                               resolution=1, showvalue=0, length=100)
        black_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        black_spinbox = ttk.Spinbox(black_frame, from_=0, to=255, 
                                   textvariable=self.black_var, width=5,
                                   command=self.on_black_spinbox_change)
        black_spinbox.grid(row=0, column=1)
        black_spinbox.bind('<Return>', self.on_black_enter)
        
        ttk.Button(adjustments_frame, text="↺", command=self.reset_black_level, width=3).grid(row=1, column=2)
        
        # Gamma
        ttk.Label(adjustments_frame, text="Gamma:").grid(row=2, column=0, sticky=tk.W)
        
        gamma_frame = ttk.Frame(adjustments_frame)
        gamma_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        gamma_frame.columnconfigure(0, weight=1)
        
        self.gamma_var = tk.DoubleVar(value=self.gamma)
        gamma_slider = tk.Scale(gamma_frame, from_=0.1, to=3.0, variable=self.gamma_var, 
                               orient=tk.HORIZONTAL, command=self.on_gamma_change, 
                               resolution=0.1, showvalue=0, length=100)
        gamma_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        gamma_spinbox = ttk.Spinbox(gamma_frame, from_=0.1, to=3.0, 
                                   textvariable=self.gamma_var, width=5, increment=0.1,
                                   command=self.on_gamma_spinbox_change, format="%.1f")
        gamma_spinbox.grid(row=0, column=1)
        gamma_spinbox.bind('<Return>', self.on_gamma_enter)
        
        ttk.Button(adjustments_frame, text="↺", command=self.reset_gamma, width=3).grid(row=2, column=2)
        
        # White Level
        ttk.Label(adjustments_frame, text="White:").grid(row=3, column=0, sticky=tk.W)
        
        white_frame = ttk.Frame(adjustments_frame)
        white_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        white_frame.columnconfigure(0, weight=1)
        
        self.white_var = tk.IntVar(value=self.white_level)
        white_slider = tk.Scale(white_frame, from_=0, to=255, variable=self.white_var, 
                               orient=tk.HORIZONTAL, command=self.on_white_change, 
                               resolution=1, showvalue=0, length=100)
        white_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        white_spinbox = ttk.Spinbox(white_frame, from_=0, to=255, 
                                   textvariable=self.white_var, width=5,
                                   command=self.on_white_spinbox_change)
        white_spinbox.grid(row=0, column=1)
        white_spinbox.bind('<Return>', self.on_white_enter)
        
        ttk.Button(adjustments_frame, text="↺", command=self.reset_white_level, width=3).grid(row=3, column=2)
        
        # Basic Adjustments Section
        basic_label = ttk.Label(adjustments_frame, text="Basic Adjustments", font=('Arial', 9, 'bold'))
        basic_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        
        # Brightness
        ttk.Label(adjustments_frame, text="Brightness:").grid(row=5, column=0, sticky=tk.W)
        
        brightness_frame = ttk.Frame(adjustments_frame)
        brightness_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        brightness_frame.columnconfigure(0, weight=1)
        
        self.brightness_var = tk.IntVar(value=self.brightness)
        brightness_slider = tk.Scale(brightness_frame, from_=-100, to=100, variable=self.brightness_var, 
                                    orient=tk.HORIZONTAL, command=self.on_brightness_change, 
                                    resolution=1, showvalue=0, length=100)
        brightness_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        brightness_spinbox = ttk.Spinbox(brightness_frame, from_=-100, to=100, 
                                        textvariable=self.brightness_var, width=5,
                                        command=self.on_brightness_spinbox_change)
        brightness_spinbox.grid(row=0, column=1)
        brightness_spinbox.bind('<Return>', self.on_brightness_enter)
        
        ttk.Button(adjustments_frame, text="↺", command=self.reset_brightness, width=3).grid(row=5, column=2)
        
        # Contrast
        ttk.Label(adjustments_frame, text="Contrast:").grid(row=6, column=0, sticky=tk.W)
        
        contrast_frame = ttk.Frame(adjustments_frame)
        contrast_frame.grid(row=6, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        contrast_frame.columnconfigure(0, weight=1)
        
        self.contrast_var = tk.IntVar(value=self.contrast)
        contrast_slider = tk.Scale(contrast_frame, from_=-100, to=100, variable=self.contrast_var, 
                                  orient=tk.HORIZONTAL, command=self.on_contrast_change, 
                                  resolution=1, showvalue=0, length=100)
        contrast_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        contrast_spinbox = ttk.Spinbox(contrast_frame, from_=-100, to=100, 
                                      textvariable=self.contrast_var, width=5,
                                      command=self.on_contrast_spinbox_change)
        contrast_spinbox.grid(row=0, column=1)
        contrast_spinbox.bind('<Return>', self.on_contrast_enter)
        
        ttk.Button(adjustments_frame, text="↺", command=self.reset_contrast, width=3).grid(row=6, column=2)
        
        # Reset All button
        ttk.Button(adjustments_frame, text="Reset All", command=self.reset_all_adjustments).grid(row=7, column=0, columnspan=3, pady=(15, 0))
        
        # Configure column weights for adjustments frame
        adjustments_frame.columnconfigure(1, weight=1)
        
        # Section 3: Controls (right part of ASCII viewer width - column 3)
        controls_frame = ttk.LabelFrame(main_frame, text="Controls", padding="5")
        controls_frame.grid(row=1, column=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2, 0), pady=(0, 10))
        
        # ASCII Width
        ttk.Label(controls_frame, text="ASCII Width:").grid(row=0, column=0, sticky=tk.W, pady=(0, 3))
        width_frame = ttk.Frame(controls_frame)
        width_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        width_frame.columnconfigure(0, weight=1)
        
        self.width_var = tk.IntVar(value=80)
        width_slider = tk.Scale(width_frame, from_=20, to=200, 
                              variable=self.width_var, orient=tk.HORIZONTAL,
                              command=self.on_width_slider_move, resolution=1, showvalue=0)
        width_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        width_spinbox = ttk.Spinbox(width_frame, from_=20, to=200, 
                                   textvariable=self.width_var, width=5,
                                   command=self.on_width_spinbox_change)
        width_spinbox.grid(row=0, column=1)
        width_spinbox.bind('<Return>', self.on_width_enter)
        
        # Aspect Ratio
        ttk.Label(controls_frame, text="Aspect Ratio (%):").grid(row=2, column=0, sticky=tk.W, pady=(10, 3))
        aspect_frame = ttk.Frame(controls_frame)
        aspect_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        aspect_frame.columnconfigure(0, weight=1)
        
        self.aspect_var = tk.IntVar(value=self.aspect_ratio)
        aspect_slider = tk.Scale(aspect_frame, from_=30, to=200, 
                                variable=self.aspect_var, orient=tk.HORIZONTAL,
                                command=self.on_aspect_slider_move, resolution=1, showvalue=0)
        aspect_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        aspect_spinbox = ttk.Spinbox(aspect_frame, from_=30, to=200, 
                                    textvariable=self.aspect_var, width=5,
                                    command=self.on_aspect_spinbox_change)
        aspect_spinbox.grid(row=0, column=1, padx=(0, 5))
        aspect_spinbox.bind('<Return>', self.on_aspect_enter)
        
        # Aspect ratio reset button
        ttk.Button(aspect_frame, text="↺", command=self.reset_aspect_ratio, width=3).grid(row=0, column=2)
        
        # ASCII Mode
        ttk.Label(controls_frame, text="ASCII Mode:").grid(row=4, column=0, sticky=tk.W, pady=(0, 3))
        self.ascii_mode_var = tk.StringVar(value=self.current_ascii_set)
        ascii_mode_combo = ttk.Combobox(controls_frame, textvariable=self.ascii_mode_var, 
                                       values=list(self.ascii_sets.keys()), 
                                       state="readonly", width=15)
        ascii_mode_combo.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ascii_mode_combo.bind('<<ComboboxSelected>>', self.on_ascii_mode_change)
        
        # Invert Colors
        self.invert_var = tk.BooleanVar(value=self.invert_colors)
        invert_checkbox = ttk.Checkbutton(controls_frame, text="Invert Colors", 
                                         variable=self.invert_var, command=self.on_invert_change)
        invert_checkbox.grid(row=6, column=0, sticky=tk.W)
        
        # === MIDDLE ROW - 2 EQUAL COLUMNS (VIEWERS) ===
        
        # Add a 4th column for proper 1:1 viewer layout
        main_frame.columnconfigure(3, weight=1)  # Add 4th column same weight as column 0
        
        # Image display frame (left side) - spans only columns 0-1 (1.5 width total)
        image_frame = ttk.LabelFrame(main_frame, text="Original Image", padding="10")
        image_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 2))
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
        
        # Image canvas with scrollbars
        self.image_canvas = tk.Canvas(image_frame, bg='white', relief=tk.SUNKEN, borderwidth=2)
        image_v_scrollbar = ttk.Scrollbar(image_frame, orient=tk.VERTICAL, command=self.image_canvas.yview)
        image_h_scrollbar = ttk.Scrollbar(image_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        self.image_canvas.configure(yscrollcommand=image_v_scrollbar.set, 
                                   xscrollcommand=image_h_scrollbar.set)
        
        self.image_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        image_v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        image_h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # ASCII display frame (right side) - spans columns 2-3 (1.5 width total)
        ascii_frame = ttk.LabelFrame(main_frame, text="ASCII Art", padding="10")
        ascii_frame.grid(row=2, column=2, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2, 0))
        ascii_frame.columnconfigure(0, weight=1)
        ascii_frame.rowconfigure(0, weight=1)
        
        # ASCII text display
        self.ascii_display = scrolledtext.ScrolledText(ascii_frame, 
                                                      font=('Courier', self.ascii_font_size),
                                                      wrap=tk.NONE,
                                                      state='disabled',
                                                      width=1,
                                                      height=1)
        self.ascii_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # === BOTTOM ROW - 2 COLUMNS (CONTROLS) ===
        
        # Image Controls (left) - spans columns 0-1
        image_controls = ttk.Frame(main_frame, padding="5")
        image_controls.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 2), pady=(5, 0))
        
        ttk.Button(image_controls, text="Select Image", command=self.select_image).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(image_controls, text="In", command=self.zoom_in_image, width=4).grid(row=0, column=1, padx=(0, 2))
        ttk.Button(image_controls, text="Out", command=self.zoom_out_image, width=4).grid(row=0, column=2, padx=(0, 2))
        ttk.Button(image_controls, text="Reset", command=self.reset_image_zoom, width=6).grid(row=0, column=3)
        
        # ASCII Controls (right) - spans columns 2-3
        ascii_controls = ttk.Frame(main_frame, padding="5")
        ascii_controls.grid(row=3, column=2, columnspan=2, sticky=(tk.W, tk.E), padx=(2, 0), pady=(5, 0))
        
        self.save_btn = ttk.Button(ascii_controls, text="Save ASCII", command=self.save_ascii, state='disabled')
        self.save_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.copy_btn = ttk.Button(ascii_controls, text="Copy to Clipboard", command=self.copy_to_clipboard, state='disabled')
        self.copy_btn.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(ascii_controls, text="In", command=self.zoom_in_ascii, width=4).grid(row=0, column=2, padx=(0, 2))
        ttk.Button(ascii_controls, text="Out", command=self.zoom_out_ascii, width=4).grid(row=0, column=3, padx=(0, 2))
        ttk.Button(ascii_controls, text="Reset", command=self.reset_ascii_zoom, width=6).grid(row=0, column=4)
    
    def update_histogram(self, image):
        """Update the histogram display"""
        self.hist_canvas.delete("all")
        
        # Get actual canvas size
        self.hist_canvas.update_idletasks()  # Ensure geometry is calculated
        canvas_width = self.hist_canvas.winfo_width()
        canvas_height = self.hist_canvas.winfo_height()
        
        # Use minimum size if canvas isn't properly sized yet
        if canvas_width <= 1:
            canvas_width = 300
        if canvas_height <= 1:
            canvas_height = 150
            
        margin = 20
        
        if image is not None:
            # Convert to grayscale and get histogram
            gray_image = ImageOps.grayscale(image)
            hist, bins = np.histogram(np.array(gray_image), bins=64, range=(0, 256))  # 64 bins for simplicity
            
            if max(hist) > 0:
                # Normalize histogram to fit canvas
                max_height = canvas_height - 2 * margin
                normalized_hist = [int((h / max(hist)) * max_height) for h in hist]
                
                # Draw histogram bars
                bar_width = (canvas_width - 2 * margin) / len(hist)
                for i, height in enumerate(normalized_hist):
                    x1 = margin + i * bar_width
                    x2 = x1 + bar_width
                    y1 = canvas_height - margin
                    y2 = y1 - height
                    
                    self.hist_canvas.create_rectangle(x1, y1, x2, y2, fill='gray', outline='gray')
                
                # Draw grid lines
                for i in range(5):  # 5 horizontal grid lines
                    y = margin + i * (canvas_height - 2 * margin) / 4
                    self.hist_canvas.create_line(margin, y, canvas_width - margin, y, fill='lightgray', width=1)
                
                for i in range(5):  # 5 vertical grid lines
                    x = margin + i * (canvas_width - 2 * margin) / 4
                    self.hist_canvas.create_line(x, margin, x, canvas_height - margin, fill='lightgray', width=1)
                
                # Add labels
                self.hist_canvas.create_text(canvas_width//2, canvas_height - 5, text="Pixel Values (0-255)", font=('Arial', 8))
                self.hist_canvas.create_text(10, canvas_height//2, text="Count", font=('Arial', 8), angle=90)
                
                # Add value labels
                self.hist_canvas.create_text(margin, canvas_height - margin + 10, text="0", font=('Arial', 7))
                self.hist_canvas.create_text(canvas_width - margin, canvas_height - margin + 10, text="255", font=('Arial', 7))
        else:
            # Empty histogram message
            self.hist_canvas.create_text(canvas_width//2, canvas_height//2, text="No Image", 
                                       font=('Arial', 12), fill='gray')
    
    def on_histogram_resize(self, event):
        """Handle histogram canvas resize"""
        # Store current image for redraw
        if hasattr(self, 'original_image') and self.original_image:
            # Redraw histogram with adjusted image if adjustments are applied
            adjusted_image = self.apply_adjustments(self.original_image)
            self.update_histogram(adjusted_image)
        else:
            self.update_histogram(None)
    
    def select_image(self):
        """Open file dialog to select an image"""
        filetypes = [
            ('All Images', '*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp'),
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg *.jpeg'),
            ('GIF files', '*.gif'),
            ('BMP files', '*.bmp'),
            ('TIFF files', '*.tiff'),
            ('WebP files', '*.webp'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Select an image",
            filetypes=filetypes
        )
        
        if filename:
            try:
                self.load_image(filename)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def load_image(self, filepath):
        """Load and display the selected image"""
        raw_image = Image.open(filepath)
        
        # Convert to RGB if necessary
        if raw_image.mode != 'RGB':
            raw_image = raw_image.convert('RGB')
        
        # Intelligently downsize for performance while preserving ASCII quality
        self.original_image = self.optimize_image_for_ascii(raw_image)
        
        # Update histogram
        self.update_histogram(self.original_image)
        
        # Display image in canvas
        self.display_image()
        
        # Auto-convert to ASCII
        self.convert_to_ascii()
        
        # Enable save and copy buttons
        self.save_btn.config(state='normal')
        self.copy_btn.config(state='normal')
    
    def optimize_image_for_ascii(self, image):
        """Intelligently downsize image for optimal ASCII conversion performance"""
        width, height = image.size
        
        # Calculate optimal size based on ASCII output requirements
        # ASCII art typically maxes out at 200 characters wide (our slider max)
        # So we never need more than ~4x this resolution for quality
        max_ascii_width = 200
        optimal_pixel_width = max_ascii_width * 4  # 800px max width
        
        # For height, maintain aspect ratio but cap at reasonable size
        aspect_ratio = height / width
        optimal_pixel_height = int(optimal_pixel_width * aspect_ratio)
        
        # Cap height to prevent extremely tall images from being too large
        max_pixel_height = 1200
        if optimal_pixel_height > max_pixel_height:
            optimal_pixel_height = max_pixel_height
            optimal_pixel_width = int(max_pixel_height / aspect_ratio)
        
        # Only downsize if the image is larger than optimal size
        if width > optimal_pixel_width or height > optimal_pixel_height:
            # Use high-quality resampling to preserve detail for ASCII conversion
            optimized = image.resize((optimal_pixel_width, optimal_pixel_height), Image.Resampling.LANCZOS)
            
            # Update window title to show optimization
            self.root.title(f"ASCII Painter - Optimized: {width}x{height} → {optimal_pixel_width}x{optimal_pixel_height}")
            
            return optimized
        else:
            # Image is already small enough, use as-is
            self.root.title(f"ASCII Painter - Original: {width}x{height}")
            return image
    
    def display_image(self):
        """Display the original image in the canvas"""
        self.update_image_display()
    
    def convert_to_ascii(self):
        """Convert the image to ASCII art"""
        if not self.original_image:
            return
        
        try:
            width = self.width_var.get()
            # Width is already validated by slider range (20-200)
            self.ascii_text = self.image_to_ascii(self.original_image, width)
            
            # Display ASCII art
            self.ascii_display.config(state='normal')
            self.ascii_display.delete(1.0, tk.END)
            self.ascii_display.insert(1.0, self.ascii_text)
            self.ascii_display.config(state='disabled')
            
            # Enable save and copy buttons
            self.save_btn.config(state='normal')
            self.copy_btn.config(state='normal')
            
        except Exception:
            # Silently handle conversion errors
            pass
    
    def image_to_ascii(self, image, width=80):
        """Convert PIL Image to ASCII art"""
        # Apply image adjustments first
        adjusted_image = self.apply_adjustments(image)
        
        # Calculate height to maintain aspect ratio
        aspect_ratio = adjusted_image.height / adjusted_image.width
        # Apply character height compensation (0.55) and user's aspect ratio percentage
        # UI shows 100% = "normal", but internally applies 0.55 base compensation
        height = int(width * aspect_ratio * 0.55 * (self.aspect_ratio / 100))
        
        # Resize image
        resized = adjusted_image.resize((width, height))
        
        # Convert to grayscale
        grayscale = ImageOps.grayscale(resized)
        
        # Convert to ASCII
        ascii_lines = []
        for y in range(height):
            line = ""
            for x in range(width):
                pixel_value = grayscale.getpixel((x, y))
                # Map pixel value (0-255) to ASCII character index
                if self.invert_colors:
                    # Normal mapping (bright pixels -> light characters)
                    char_index = int(pixel_value / 255 * (len(self.ascii_chars) - 1))
                else:
                    # Inverted mapping (bright pixels -> dark characters)
                    char_index = int((255 - pixel_value) / 255 * (len(self.ascii_chars) - 1))
                line += self.ascii_chars[char_index]
            ascii_lines.append(line)
        
        return '\n'.join(ascii_lines)
    
    def save_ascii(self):
        """Save ASCII art to a text file"""
        if not self.ascii_text:
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save ASCII Art",
            defaultextension=".txt",
            filetypes=[('Text files', '*.txt'), ('All files', '*.*')]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.ascii_text)
                messagebox.showinfo("Success", "ASCII art saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def copy_to_clipboard(self):
        """Copy ASCII art to clipboard"""
        if not self.ascii_text:
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(self.ascii_text)
        messagebox.showinfo("Success", "ASCII art copied to clipboard!")
    
    def zoom_in_image(self):
        """Zoom in on the original image"""
        self.image_zoom *= 1.2
        self.update_image_display()
    
    def zoom_out_image(self):
        """Zoom out on the original image"""
        self.image_zoom /= 1.2
        self.update_image_display()
    
    def reset_image_zoom(self):
        """Reset image zoom to original size"""
        self.image_zoom = 1.0
        self.update_image_display()
    
    def update_image_display(self):
        """Update the image display with current zoom level"""
        if not self.original_image:
            return
        
        try:
            # Calculate display size with zoom (base size 400px, then apply zoom)
            base_size = 400
            max_size = int(base_size * self.image_zoom)
            display_image = self.original_image.copy()
            
            # Calculate proportional size while maintaining aspect ratio
            original_width, original_height = self.original_image.size
            if original_width > original_height:
                new_width = max_size
                new_height = int((original_height / original_width) * max_size)
            else:
                new_height = max_size
                new_width = int((original_width / original_height) * max_size)
            
            display_image = display_image.resize((new_width, new_height))
            
            # Save to temporary file and load with tkinter PhotoImage
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                display_image.save(tmp.name, 'PNG')
                temp_path = tmp.name
            
            # Use tkinter's PhotoImage
            self.photo_image = tk.PhotoImage(file=temp_path)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            # Clear canvas and add image
            self.image_canvas.delete("all")
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
            
            # Update scroll region to match the actual image size
            self.image_canvas.configure(scrollregion=(0, 0, new_width, new_height))
            
        except Exception as e:
            # Fallback to text display if image preview fails
            self.image_canvas.delete("all")
            info_text = f"Image loaded: {self.original_image.size[0]}x{self.original_image.size[1]}\n"
            info_text += f"Zoom: {self.image_zoom:.1f}x\n"
            info_text += f"Ready to convert to ASCII"
            
            self.image_canvas.create_text(
                200, 100, 
                text=info_text,
                font=('Arial', 12),
                fill='black',
                anchor='center'
            )
    
    def zoom_in_ascii(self):
        """Zoom in on the ASCII art"""
        self.ascii_font_size = min(self.ascii_font_size + 2, 24)
        self.update_ascii_display()
        self.save_preferences()
    
    def zoom_out_ascii(self):
        """Zoom out on the ASCII art"""
        self.ascii_font_size = max(self.ascii_font_size - 2, 4)
        self.update_ascii_display()
        self.save_preferences()
    
    def reset_ascii_zoom(self):
        """Reset ASCII zoom to original size"""
        self.ascii_font_size = 8
        self.update_ascii_display()
        self.save_preferences()
    
    def update_ascii_display(self):
        """Update the ASCII display with current font size"""
        if not self.ascii_text:
            return
        
        # Update font size only, preserving content and layout
        self.ascii_display.config(font=('Courier', self.ascii_font_size))
    
    def on_ascii_mode_change(self, event=None):
        """Handle ASCII mode selection change"""
        self.current_ascii_set = self.ascii_mode_var.get()
        self.ascii_chars = self.ascii_sets[self.current_ascii_set]
        self.save_preferences()
        
        # Auto-convert if image is loaded
        if self.original_image:
            self.convert_to_ascii()
    
    def on_width_slider_move(self, value):
        """Handle real-time slider movement with conversion"""
        # Convert in real-time as slider moves
        if self.original_image:
            self.convert_to_ascii()
    
    def on_width_enter(self, event):
        """Handle Enter key in width spinbox (triggers conversion)"""
        if self.original_image:
            self.convert_to_ascii()
    
    def on_width_spinbox_change(self):
        """Handle spinbox up/down arrows (triggers conversion)"""
        if self.original_image:
            self.convert_to_ascii()
    
    def on_invert_change(self):
        """Handle invert colors checkbox change"""
        self.invert_colors = self.invert_var.get()
        self.save_preferences()
        
        # Auto-convert if image is loaded
        if self.original_image:
            self.convert_to_ascii()
    
    def on_aspect_slider_move(self, value):
        """Handle real-time aspect ratio slider movement with conversion"""
        self.aspect_ratio = self.aspect_var.get()
        self.save_preferences()
        # Convert in real-time as slider moves
        if self.original_image:
            self.convert_to_ascii()
    
    def on_aspect_enter(self, event):
        """Handle Enter key in aspect ratio spinbox (triggers conversion)"""
        self.aspect_ratio = self.aspect_var.get()
        self.save_preferences()
        if self.original_image:
            self.convert_to_ascii()
    
    def on_aspect_spinbox_change(self):
        """Handle spinbox up/down arrows (triggers conversion)"""
        self.aspect_ratio = self.aspect_var.get()
        self.save_preferences()
        if self.original_image:
            self.convert_to_ascii()
    
    # Reset methods
    def reset_aspect_ratio(self):
        """Reset aspect ratio to 100%"""
        self.aspect_ratio = 100
        self.aspect_var.set(100)
        self.save_preferences()
        if self.original_image:
            self.convert_to_ascii()
    
    # Image adjustment callbacks
    def on_black_change(self, value):
        """Handle black level change"""
        self.black_level = self.black_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_white_change(self, value):
        """Handle white level change"""
        self.white_level = self.white_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_gamma_change(self, value):
        """Handle gamma change"""
        self.gamma = self.gamma_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_brightness_change(self, value):
        """Handle brightness change"""
        self.brightness = self.brightness_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_contrast_change(self, value):
        """Handle contrast change"""
        self.contrast = self.contrast_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    # Spinbox and Enter key methods for all adjustments
    def on_black_spinbox_change(self):
        """Handle black level spinbox up/down arrows"""
        self.black_level = self.black_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_black_enter(self, event):
        """Handle Enter key in black level spinbox"""
        self.black_level = self.black_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_gamma_spinbox_change(self):
        """Handle gamma spinbox up/down arrows"""
        self.gamma = self.gamma_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_gamma_enter(self, event):
        """Handle Enter key in gamma spinbox"""
        self.gamma = self.gamma_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_white_spinbox_change(self):
        """Handle white level spinbox up/down arrows"""
        self.white_level = self.white_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_white_enter(self, event):
        """Handle Enter key in white level spinbox"""
        self.white_level = self.white_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_brightness_spinbox_change(self):
        """Handle brightness spinbox up/down arrows"""
        self.brightness = self.brightness_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_brightness_enter(self, event):
        """Handle Enter key in brightness spinbox"""
        self.brightness = self.brightness_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_contrast_spinbox_change(self):
        """Handle contrast spinbox up/down arrows"""
        self.contrast = self.contrast_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def on_contrast_enter(self, event):
        """Handle Enter key in contrast spinbox"""
        self.contrast = self.contrast_var.get()
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    # Reset methods for adjustments
    def reset_black_level(self):
        """Reset black level to 0"""
        self.black_level = 0
        self.black_var.set(0)
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def reset_white_level(self):
        """Reset white level to 255"""
        self.white_level = 255
        self.white_var.set(255)
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def reset_gamma(self):
        """Reset gamma to 1.0"""
        self.gamma = 1.0
        self.gamma_var.set(1.0)
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def reset_brightness(self):
        """Reset brightness to 0"""
        self.brightness = 0
        self.brightness_var.set(0)
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def reset_contrast(self):
        """Reset contrast to 0"""
        self.contrast = 0
        self.contrast_var.set(0)
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def reset_all_adjustments(self):
        """Reset all image adjustments to defaults"""
        self.black_level = 0
        self.white_level = 255
        self.gamma = 1.0
        self.brightness = 0
        self.contrast = 0
        
        self.black_var.set(0)
        self.white_var.set(255)
        self.gamma_var.set(1.0)
        self.brightness_var.set(0)
        self.contrast_var.set(0)
        
        self.save_preferences()
        if self.original_image:
            self.update_histogram(self.apply_adjustments(self.original_image))
            self.convert_to_ascii()
    
    def apply_adjustments(self, image):
        """Apply all image adjustments to the image"""
        if image is None:
            return None
        
        # Check if adjustments are at default values to skip processing
        if (self.black_level == 0 and self.white_level == 255 and 
            self.gamma == 1.0 and self.brightness == 0 and self.contrast == 0):
            return image
        
        # Convert to numpy array for processing
        img_array = np.array(image).astype(np.float32)
        
        # Apply levels (black, gamma, white)
        if self.black_level != 0 or self.white_level != 255:
            # Normalize to 0-1 range based on black/white levels
            img_array = np.clip((img_array - self.black_level) / (self.white_level - self.black_level), 0, 1)
        else:
            img_array = img_array / 255.0
        
        # Apply gamma correction
        if self.gamma != 1.0:
            img_array = np.power(img_array, 1.0/self.gamma)
        
        # Apply brightness (-100 to +100 -> -0.5 to +0.5 adjustment)
        if self.brightness != 0:
            brightness_factor = self.brightness / 200.0
            img_array = img_array + brightness_factor
        
        # Apply contrast (-100 to +100 -> 0.0 to 2.0 multiplier)
        if self.contrast != 0:
            contrast_factor = (self.contrast + 100) / 100.0
            img_array = (img_array - 0.5) * contrast_factor + 0.5
        
        # Clamp to valid range and convert back to 0-255
        img_array = np.clip(img_array * 255, 0, 255).astype(np.uint8)
        
        # Convert back to PIL Image
        return Image.fromarray(img_array)
    
    def load_preferences(self):
        """Load user preferences from config file"""
        try:
            with open('ascii_painter_config.json', 'r') as f:
                config = json.load(f)
                self.current_ascii_set = config.get('ascii_set', '16-Level Alternative (Smoother)')
                self.ascii_font_size = config.get('font_size', 8)
                self.invert_colors = config.get('invert_colors', False)
                self.aspect_ratio = config.get('aspect_ratio', 100)
                self.black_level = config.get('black_level', 0)
                self.white_level = config.get('white_level', 255)
                self.gamma = config.get('gamma', 1.0)
                self.brightness = config.get('brightness', 0)
                self.contrast = config.get('contrast', 0)
                self.ascii_chars = self.ascii_sets.get(self.current_ascii_set, self.ascii_sets['16-Level Alternative (Smoother)'])
        except (FileNotFoundError, json.JSONDecodeError):
            # Use defaults if no config file or corrupted file
            pass
    
    def save_preferences(self):
        """Save user preferences to config file"""
        try:
            config = {
                'ascii_set': self.current_ascii_set,
                'font_size': self.ascii_font_size,
                'invert_colors': self.invert_colors,
                'aspect_ratio': self.aspect_ratio,
                'black_level': self.black_level,
                'white_level': self.white_level,
                'gamma': self.gamma,
                'brightness': self.brightness,
                'contrast': self.contrast
            }
            with open('ascii_painter_config.json', 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            # Silently fail if can't save preferences
            pass

def main():
    root = tk.Tk()
    app = ASCIIPainter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
