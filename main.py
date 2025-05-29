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
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.columnconfigure(3, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="ASCII Painter", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        # Group 1: File Operations
        file_ops = ttk.LabelFrame(main_frame, text="File Operations", padding="5")
        file_ops.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 5), pady=(0, 10))
        
        self.select_btn = ttk.Button(file_ops, text="Select Image", command=self.select_image)
        self.select_btn.grid(row=0, column=0, pady=(0, 3), sticky=(tk.W, tk.E))
        
        self.save_btn = ttk.Button(file_ops, text="Save ASCII", command=self.save_ascii, state='disabled')
        self.save_btn.grid(row=1, column=0, pady=(0, 3), sticky=(tk.W, tk.E))
        
        self.copy_btn = ttk.Button(file_ops, text="Copy to Clipboard", command=self.copy_to_clipboard, state='disabled')
        self.copy_btn.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        
        # Group 3: ASCII Controls
        ascii_controls = ttk.LabelFrame(main_frame, text="ASCII Controls", padding="5")
        ascii_controls.grid(row=1, column=2, sticky=(tk.W, tk.E), padx=(0, 5), pady=(0, 10))
        
        ttk.Label(ascii_controls, text="ASCII Width:").grid(row=0, column=0, sticky=tk.W, pady=(0, 3))
        
        # Width controls with slider and spinbox
        width_frame = ttk.Frame(ascii_controls)
        width_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        width_frame.columnconfigure(0, weight=1)
        
        self.width_var = tk.IntVar(value=80)
        
        # Real-time slider
        width_slider = tk.Scale(width_frame, from_=20, to=200, 
                              variable=self.width_var, orient=tk.HORIZONTAL,
                              command=self.on_width_slider_move,
                              resolution=1,  # Integer values only
                              showvalue=0)   # Hide value display (spinbox shows it)
        width_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Spinbox for precise entry (Enter to apply)
        width_spinbox = ttk.Spinbox(width_frame, from_=20, to=200, 
                                   textvariable=self.width_var, width=5,
                                   command=self.on_width_spinbox_change)
        width_spinbox.grid(row=0, column=1)
        width_spinbox.bind('<Return>', self.on_width_enter)
        
        ttk.Label(ascii_controls, text="ASCII Mode:").grid(row=2, column=0, sticky=tk.W, pady=(0, 3))
        self.ascii_mode_var = tk.StringVar(value=self.current_ascii_set)
        ascii_mode_combo = ttk.Combobox(ascii_controls, textvariable=self.ascii_mode_var, 
                                       values=list(self.ascii_sets.keys()), 
                                       state="readonly", width=20)
        ascii_mode_combo.grid(row=3, column=0, sticky=(tk.W, tk.E))
        ascii_mode_combo.bind('<<ComboboxSelected>>', self.on_ascii_mode_change)
        
        # Invert colors checkbox
        self.invert_var = tk.BooleanVar(value=self.invert_colors)
        invert_checkbox = ttk.Checkbutton(ascii_controls, text="Invert Colors", 
                                         variable=self.invert_var,
                                         command=self.on_invert_change)
        invert_checkbox.grid(row=4, column=0, sticky=tk.W, pady=(5, 0))
        
        # Aspect ratio controls
        ttk.Label(ascii_controls, text="Aspect Ratio (%):").grid(row=5, column=0, sticky=tk.W, pady=(10, 3))
        
        # Aspect ratio controls with slider and spinbox
        aspect_frame = ttk.Frame(ascii_controls)
        aspect_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        aspect_frame.columnconfigure(0, weight=1)
        
        self.aspect_var = tk.IntVar(value=self.aspect_ratio)
        
        # Real-time slider (30% to 200%)
        aspect_slider = tk.Scale(aspect_frame, from_=30, to=200, 
                                variable=self.aspect_var, orient=tk.HORIZONTAL,
                                command=self.on_aspect_slider_move,
                                resolution=1,  # Integer values only
                                showvalue=0)   # Hide value display (spinbox shows it)
        aspect_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Spinbox for precise entry (Enter to apply)
        aspect_spinbox = ttk.Spinbox(aspect_frame, from_=30, to=200, 
                                    textvariable=self.aspect_var, width=5,
                                    command=self.on_aspect_spinbox_change)
        aspect_spinbox.grid(row=0, column=1)
        aspect_spinbox.bind('<Return>', self.on_aspect_enter)
        
        
        # Image display frame (left side)
        image_frame = ttk.LabelFrame(main_frame, text="Original Image", padding="10")
        image_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
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
        
        # ASCII display frame (right side)
        ascii_frame = ttk.LabelFrame(main_frame, text="ASCII Art", padding="10")
        ascii_frame.grid(row=2, column=2, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
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
        
        # Image Viewer Control (positioned below image viewer)
        image_viewer_control = ttk.Frame(main_frame, padding="5")
        image_viewer_control.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        
        ttk.Button(image_viewer_control, text="In", command=self.zoom_in_image, width=4).grid(row=0, column=0, padx=(0, 2))
        ttk.Button(image_viewer_control, text="Out", command=self.zoom_out_image, width=4).grid(row=0, column=1, padx=(0, 2))
        ttk.Button(image_viewer_control, text="Reset", command=self.reset_image_zoom, width=6).grid(row=0, column=2)
        
        # ASCII Viewer Control (positioned below ASCII viewer)
        ascii_viewer_control = ttk.Frame(main_frame, padding="5")
        ascii_viewer_control.grid(row=3, column=2, columnspan=2, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        
        ttk.Button(ascii_viewer_control, text="In", command=self.zoom_in_ascii, width=4).grid(row=0, column=0, padx=(0, 2))
        ttk.Button(ascii_viewer_control, text="Out", command=self.zoom_out_ascii, width=4).grid(row=0, column=1, padx=(0, 2))
        ttk.Button(ascii_viewer_control, text="Reset", command=self.reset_ascii_zoom, width=6).grid(row=0, column=2)
    
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
        self.original_image = Image.open(filepath)
        
        # Convert to RGB if necessary
        if self.original_image.mode != 'RGB':
            self.original_image = self.original_image.convert('RGB')
        
        # Display image in canvas
        self.display_image()
        
        # Auto-convert to ASCII
        self.convert_to_ascii()
        
        # Enable save and copy buttons
        self.save_btn.config(state='normal')
        self.copy_btn.config(state='normal')
    
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
        # Calculate height to maintain aspect ratio
        aspect_ratio = image.height / image.width
        # Apply character height compensation (0.55) and user's aspect ratio percentage
        # UI shows 100% = "normal", but internally applies 0.55 base compensation
        height = int(width * aspect_ratio * 0.55 * (self.aspect_ratio / 100))
        
        # Resize image
        resized = image.resize((width, height))
        
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
    
    def load_preferences(self):
        """Load user preferences from config file"""
        try:
            with open('ascii_painter_config.json', 'r') as f:
                config = json.load(f)
                self.current_ascii_set = config.get('ascii_set', '16-Level Alternative (Smoother)')
                self.ascii_font_size = config.get('font_size', 8)
                self.invert_colors = config.get('invert_colors', False)
                self.aspect_ratio = config.get('aspect_ratio', 100)
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
                'aspect_ratio': self.aspect_ratio
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
