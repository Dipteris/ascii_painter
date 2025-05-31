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
import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# UI Constants
class UIConstants:
    """Constants for UI layout and behavior"""
    WINDOW_SIZE = "1500x1000"
    WINDOW_BG = '#f0f0f0'
    TITLE_FONT = ('Arial', 16, 'bold')
    SECTION_FONT = ('Arial', 9, 'bold')
    HIST_FONT = ('Arial', 8)
    LABEL_FONT = ('Arial', 7)
    ASCII_FONT = 'Courier'
    
    # Zoom and sizing
    ZOOM_FACTOR = 1.2
    BASE_IMAGE_SIZE = 400
    MIN_FONT_SIZE = 4
    MAX_FONT_SIZE = 24
    DEFAULT_FONT_SIZE = 8
    
    # Image optimization
    MAX_ASCII_WIDTH = 200
    OPTIMAL_PIXEL_MULTIPLIER = 4
    MAX_PIXEL_HEIGHT = 1200
    
    # Histogram
    HIST_BINS = 64
    HIST_MARGIN = 20
    HIST_GRID_LINES = 5
    
    # Character height compensation
    CHAR_HEIGHT_COMPENSATION = 0.55


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle and log errors in methods"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            if hasattr(self, 'root'):
                messagebox.showerror("Error", f"An error occurred in {func.__name__}: {str(e)}")
            raise
    return wrapper

class ASCIIPainter:
    """Main application class for ASCII Painter.
    
    A GUI application that converts images to ASCII art with professional
    image adjustment capabilities including levels, gamma, brightness, and contrast.
    """
    
    def __init__(self, root: tk.Tk) -> None:
        """Initialize the ASCII Painter application.
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.root.title("ASCII Painter")
        self.root.geometry(UIConstants.WINDOW_SIZE)
        self.root.configure(bg=UIConstants.WINDOW_BG)
        
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
        self.original_image: Optional[Image.Image] = None
        self.ascii_text: str = ""
        
        # Zoom settings
        self.image_zoom: float = 1.0
        self.ascii_font_size: int = UIConstants.DEFAULT_FONT_SIZE
        
        
        # Load preferences
        self.load_preferences()
        
        self.setup_ui()
    
    def _create_adjustment_handler(self, attr_name: str, var_obj: tk.Variable) -> Dict[str, Callable]:
        """Create standardized handlers for adjustment controls.
        
        Args:
            attr_name: Name of the attribute to update
            var_obj: Tkinter variable object
            
        Returns:
            Dictionary containing slider, spinbox, and enter event handlers
        """
        def slider_handler(value):
            setattr(self, attr_name, var_obj.get())
            self.save_preferences()
            if self.original_image:
                self.update_histogram(self.apply_adjustments(self.original_image))
                self.convert_to_ascii()
        
        def spinbox_handler():
            setattr(self, attr_name, var_obj.get())
            self.save_preferences()
            if self.original_image:
                self.update_histogram(self.apply_adjustments(self.original_image))
                self.convert_to_ascii()
        
        def enter_handler(event):
            setattr(self, attr_name, var_obj.get())
            self.save_preferences()
            if self.original_image:
                self.update_histogram(self.apply_adjustments(self.original_image))
                self.convert_to_ascii()
        
        return {
            'slider': slider_handler,
            'spinbox': spinbox_handler,
            'enter': enter_handler
        }
    
    def setup_ui(self) -> None:
        """Set up the main user interface."""
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
                               font=UIConstants.TITLE_FONT)
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        # Initialize Tkinter variables for UI controls
        self.black_var = tk.IntVar(value=self.black_level)
        self.white_var = tk.IntVar(value=self.white_level)
        self.gamma_var = tk.DoubleVar(value=self.gamma)
        self.brightness_var = tk.IntVar(value=self.brightness)
        self.contrast_var = tk.IntVar(value=self.contrast)
        
        # Set up the three main sections
        self._setup_histogram_section(main_frame)
        self._setup_adjustments_section(main_frame)
        self._setup_controls_section(main_frame)
        self._setup_viewer_sections(main_frame)
        self._setup_control_buttons(main_frame)
    
    def _setup_histogram_section(self, parent: ttk.Frame) -> None:
        """Set up the histogram display section."""
        # Section 1: Histogram (matches Original Image width - spans columns 0-1)
        histogram_frame = ttk.LabelFrame(parent, text="Histogram", padding="5")
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
    
    def _setup_adjustments_section(self, parent: ttk.Frame) -> None:
        """Set up the image adjustments section."""
        # Section 2: Image Adjustments (left part of ASCII viewer width - column 2)
        adjustments_frame = ttk.LabelFrame(parent, text="Image Adjustments", padding="5")
        adjustments_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2, 2), pady=(0, 10))
        
        self._setup_levels_controls(adjustments_frame)
        self._setup_basic_adjustments(adjustments_frame)
        
        # Reset All button
        ttk.Button(adjustments_frame, text="Reset All", command=self.reset_all_adjustments).grid(row=7, column=0, columnspan=3, pady=(15, 0))
        
        # Configure column weights for adjustments frame
        adjustments_frame.columnconfigure(1, weight=1)
    
    def _setup_levels_controls(self, parent: ttk.Frame) -> None:
        """Set up the levels control section."""
        # Levels Section
        levels_label = ttk.Label(parent, text="Levels", font=UIConstants.SECTION_FONT)
        levels_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Create handlers for all adjustments
        black_handlers = self._create_adjustment_handler('black_level', self.black_var)
        gamma_handlers = self._create_adjustment_handler('gamma', self.gamma_var)
        white_handlers = self._create_adjustment_handler('white_level', self.white_var)
        
        # Black Level
        self._create_adjustment_control(parent, "Black:", 1, 0, 255, self.black_var, 
                                      black_handlers, self.reset_black_level, resolution=1)
        
        # Gamma
        self._create_adjustment_control(parent, "Gamma:", 2, 0.1, 3.0, self.gamma_var,
                                      gamma_handlers, self.reset_gamma, resolution=0.1, format_str="%.1f", increment=0.1)
        
        # White Level
        self._create_adjustment_control(parent, "White:", 3, 0, 255, self.white_var,
                                      white_handlers, self.reset_white_level, resolution=1)
    
    def _setup_basic_adjustments(self, parent: ttk.Frame) -> None:
        """Set up the basic adjustments section."""
        # Basic Adjustments Section
        basic_label = ttk.Label(parent, text="Basic Adjustments", font=UIConstants.SECTION_FONT)
        basic_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        
        # Create handlers for basic adjustments
        brightness_handlers = self._create_adjustment_handler('brightness', self.brightness_var)
        contrast_handlers = self._create_adjustment_handler('contrast', self.contrast_var)
        
        # Brightness
        self._create_adjustment_control(parent, "Brightness:", 5, -100, 100, self.brightness_var,
                                      brightness_handlers, self.reset_brightness, resolution=1)
        
        # Contrast
        self._create_adjustment_control(parent, "Contrast:", 6, -100, 100, self.contrast_var,
                                      contrast_handlers, self.reset_contrast, resolution=1)
    
    def _create_adjustment_control(self, parent: ttk.Frame, label: str, row: int, 
                                 min_val: float, max_val: float, var_obj: tk.Variable,
                                 handlers: Dict[str, Callable], reset_func: Callable,
                                 resolution: float = 1, format_str: str = None, increment: float = None) -> None:
        """Create a standardized adjustment control with slider, spinbox, and reset button."""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W)
        
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        control_frame.columnconfigure(0, weight=1)
        
        # Slider
        slider = tk.Scale(control_frame, from_=min_val, to=max_val, variable=var_obj,
                         orient=tk.HORIZONTAL, command=handlers['slider'],
                         resolution=resolution, showvalue=0, length=100)
        slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Spinbox
        spinbox_kwargs = {
            'from_': min_val,
            'to': max_val,
            'textvariable': var_obj,
            'width': 5,
            'command': handlers['spinbox']
        }
        if increment:
            spinbox_kwargs['increment'] = increment
        if format_str:
            spinbox_kwargs['format'] = format_str
            
        spinbox = ttk.Spinbox(control_frame, **spinbox_kwargs)
        spinbox.grid(row=0, column=1)
        spinbox.bind('<Return>', handlers['enter'])
        
        # Reset button
        ttk.Button(parent, text="↺", command=reset_func, width=3).grid(row=row, column=2)
    
    def _setup_controls_section(self, parent: ttk.Frame) -> None:
        """Set up the controls section."""
        # Section 3: Controls (right part of ASCII viewer width - column 3)
        controls_frame = ttk.LabelFrame(parent, text="Controls", padding="5")
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
    
    def _setup_viewer_sections(self, parent: ttk.Frame) -> None:
        """Set up the image and ASCII viewer sections."""
        # Add a 4th column for proper 1:1 viewer layout
        parent.columnconfigure(3, weight=1)  # Add 4th column same weight as column 0
        
        # Image display frame (left side) - spans only columns 0-1 (1.5 width total)
        image_frame = ttk.LabelFrame(parent, text="Original Image", padding="10")
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
        ascii_frame = ttk.LabelFrame(parent, text="ASCII Art", padding="10")
        ascii_frame.grid(row=2, column=2, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2, 0))
        ascii_frame.columnconfigure(0, weight=1)
        ascii_frame.rowconfigure(0, weight=1)
        
        # ASCII text display
        self.ascii_display = scrolledtext.ScrolledText(ascii_frame, 
                                                      font=(UIConstants.ASCII_FONT, self.ascii_font_size),
                                                      wrap=tk.NONE,
                                                      state='disabled',
                                                      width=1,
                                                      height=1)
        self.ascii_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _setup_control_buttons(self, parent: ttk.Frame) -> None:
        """Set up the control button sections."""
        # Image Controls (left) - spans columns 0-1
        image_controls = ttk.Frame(parent, padding="5")
        image_controls.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 2), pady=(5, 0))
        image_controls.columnconfigure(2, weight=1)
        
        ttk.Button(image_controls, text="Select Image", command=self.select_image).grid(row=0, column=0, padx=(0, 10))
        
        # Image Zoom Control
        ttk.Label(image_controls, text="Zoom:").grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        
        zoom_frame = ttk.Frame(image_controls)
        zoom_frame.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(0, 5))
        zoom_frame.columnconfigure(0, weight=1)
        
        self.image_zoom_var = tk.DoubleVar(value=self.image_zoom)
        image_zoom_slider = tk.Scale(zoom_frame, from_=0.1, to=5.0, variable=self.image_zoom_var,
                                   orient=tk.HORIZONTAL, command=self.on_image_zoom_change,
                                   resolution=0.1, showvalue=0)
        image_zoom_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        image_zoom_spinbox = ttk.Spinbox(zoom_frame, from_=0.1, to=5.0, 
                                       textvariable=self.image_zoom_var, width=5,
                                       command=self.on_image_zoom_spinbox_change,
                                       increment=0.1, format="%.1f")
        image_zoom_spinbox.grid(row=0, column=1)
        image_zoom_spinbox.bind('<Return>', self.on_image_zoom_enter)
        
        ttk.Button(image_controls, text="↺", command=self.reset_image_zoom, width=3).grid(row=0, column=3)
        
        # ASCII Controls (right) - spans columns 2-3
        ascii_controls = ttk.Frame(parent, padding="5")
        ascii_controls.grid(row=3, column=2, columnspan=2, sticky=(tk.W, tk.E), padx=(2, 0), pady=(5, 0))
        ascii_controls.columnconfigure(3, weight=1)
        
        self.save_btn = ttk.Button(ascii_controls, text="Save ASCII", command=self.save_ascii, state='disabled')
        self.save_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.copy_btn = ttk.Button(ascii_controls, text="Copy to Clipboard", command=self.copy_to_clipboard, state='disabled')
        self.copy_btn.grid(row=0, column=1, padx=(0, 10))
        
        # ASCII Font Size Control
        ttk.Label(ascii_controls, text="Font:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        
        font_frame = ttk.Frame(ascii_controls)
        font_frame.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 5))
        font_frame.columnconfigure(0, weight=1)
        
        self.ascii_font_var = tk.IntVar(value=self.ascii_font_size)
        ascii_font_slider = tk.Scale(font_frame, from_=UIConstants.MIN_FONT_SIZE, to=UIConstants.MAX_FONT_SIZE, 
                                   variable=self.ascii_font_var, orient=tk.HORIZONTAL, 
                                   command=self.on_ascii_font_change, resolution=1, showvalue=0)
        ascii_font_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ascii_font_spinbox = ttk.Spinbox(font_frame, from_=UIConstants.MIN_FONT_SIZE, to=UIConstants.MAX_FONT_SIZE,
                                       textvariable=self.ascii_font_var, width=3,
                                       command=self.on_ascii_font_spinbox_change)
        ascii_font_spinbox.grid(row=0, column=1)
        ascii_font_spinbox.bind('<Return>', self.on_ascii_font_enter)
        
        ttk.Button(ascii_controls, text="↺", command=self.reset_ascii_zoom, width=3).grid(row=0, column=4)
    
    @handle_errors
    def update_histogram(self, image: Optional[Image.Image]) -> None:
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
            
        margin = UIConstants.HIST_MARGIN
        
        if image is not None:
            # Convert to grayscale and get histogram
            gray_image = ImageOps.grayscale(image)
            hist, bins = np.histogram(np.array(gray_image), bins=UIConstants.HIST_BINS, range=(0, 256))
            
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
                for i in range(UIConstants.HIST_GRID_LINES):  # horizontal grid lines
                    y = margin + i * (canvas_height - 2 * margin) / (UIConstants.HIST_GRID_LINES - 1)
                    self.hist_canvas.create_line(margin, y, canvas_width - margin, y, fill='lightgray', width=1)
                
                for i in range(UIConstants.HIST_GRID_LINES):  # vertical grid lines
                    x = margin + i * (canvas_width - 2 * margin) / (UIConstants.HIST_GRID_LINES - 1)
                    self.hist_canvas.create_line(x, margin, x, canvas_height - margin, fill='lightgray', width=1)
                
                # Add labels
                self.hist_canvas.create_text(canvas_width//2, canvas_height - 5, text="Pixel Values (0-255)", font=UIConstants.HIST_FONT)
                self.hist_canvas.create_text(10, canvas_height//2, text="Count", font=UIConstants.HIST_FONT, angle=90)
                
                # Add value labels
                self.hist_canvas.create_text(margin, canvas_height - margin + 10, text="0", font=UIConstants.LABEL_FONT)
                self.hist_canvas.create_text(canvas_width - margin, canvas_height - margin + 10, text="255", font=UIConstants.LABEL_FONT)
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
        
        # Apply EXIF orientation to fix rotated images
        raw_image = ImageOps.exif_transpose(raw_image)
        
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
        # ASCII art typically maxes out at MAX_ASCII_WIDTH characters wide (our slider max)
        # So we never need more than ~4x this resolution for quality
        max_ascii_width = UIConstants.MAX_ASCII_WIDTH
        optimal_pixel_width = max_ascii_width * UIConstants.OPTIMAL_PIXEL_MULTIPLIER
        
        # For height, maintain aspect ratio but cap at reasonable size
        aspect_ratio = height / width
        optimal_pixel_height = int(optimal_pixel_width * aspect_ratio)
        
        # Cap height to prevent extremely tall images from being too large
        max_pixel_height = UIConstants.MAX_PIXEL_HEIGHT
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
            
        except Exception as e:
            logger.error(f"Failed to convert image to ASCII: {str(e)}")
            messagebox.showerror("Conversion Error", f"Failed to convert image to ASCII: {str(e)}")
    
    def image_to_ascii(self, image, width=80):
        """Convert PIL Image to ASCII art"""
        # Apply image adjustments first
        adjusted_image = self.apply_adjustments(image)
        
        # Calculate height to maintain aspect ratio
        aspect_ratio = adjusted_image.height / adjusted_image.width
        # Apply character height compensation and user's aspect ratio percentage
        # UI shows 100% = "normal", but internally applies base compensation
        height = int(width * aspect_ratio * UIConstants.CHAR_HEIGHT_COMPENSATION * (self.aspect_ratio / 100))
        
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
    
    def on_image_zoom_change(self, value):
        """Handle image zoom slider movement"""
        self.image_zoom = self.image_zoom_var.get()
        self.update_image_display()
    
    def on_image_zoom_spinbox_change(self):
        """Handle image zoom spinbox change"""
        self.image_zoom = self.image_zoom_var.get()
        self.update_image_display()
    
    def on_image_zoom_enter(self, event):
        """Handle Enter key in image zoom spinbox"""
        self.image_zoom = self.image_zoom_var.get()
        self.update_image_display()
    
    def reset_image_zoom(self):
        """Reset image zoom to original size"""
        self.image_zoom = 1.0
        self.image_zoom_var.set(1.0)
        self.update_image_display()
    
    def update_image_display(self):
        """Update the image display with current zoom level"""
        if not self.original_image:
            return
        
        try:
            # Calculate display size with zoom (base size then apply zoom)
            base_size = UIConstants.BASE_IMAGE_SIZE
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
    
    def on_ascii_font_change(self, value):
        """Handle ASCII font size slider movement"""
        self.ascii_font_size = self.ascii_font_var.get()
        self.update_ascii_display()
        self.save_preferences()
    
    def on_ascii_font_spinbox_change(self):
        """Handle ASCII font size spinbox change"""
        self.ascii_font_size = self.ascii_font_var.get()
        self.update_ascii_display()
        self.save_preferences()
    
    def on_ascii_font_enter(self, event):
        """Handle Enter key in ASCII font size spinbox"""
        self.ascii_font_size = self.ascii_font_var.get()
        self.update_ascii_display()
        self.save_preferences()
    
    @handle_errors
    def reset_ascii_zoom(self) -> None:
        """Reset ASCII zoom to original size"""
        self.ascii_font_size = UIConstants.DEFAULT_FONT_SIZE
        self.ascii_font_var.set(UIConstants.DEFAULT_FONT_SIZE)
        self.update_ascii_display()
        self.save_preferences()
    
    def update_ascii_display(self):
        """Update the ASCII display with current font size"""
        if not self.ascii_text:
            return
        
        # Update font size only, preserving content and layout
        self.ascii_display.config(font=(UIConstants.ASCII_FONT, self.ascii_font_size))
    
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
    
    # Note: Image adjustment handlers are now consolidated in the _create_adjustment_handler method
    
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
        except FileNotFoundError:
            logger.info("No config file found, using defaults")
        except json.JSONDecodeError as e:
            logger.warning(f"Corrupted config file, using defaults: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error loading preferences: {str(e)}")
    
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
            logger.warning(f"Failed to save preferences: {str(e)}")
            # Don't show error dialog for preferences - non-critical

def main():
    root = tk.Tk()
    app = ASCIIPainter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
