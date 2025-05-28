#!/usr/bin/env python3
"""
ASCII Painter - Convert images to ASCII art with GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk, ImageOps
import io
import os

class ASCIIPainter:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII Painter")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # ASCII character set (light to dark)
        self.ascii_chars = " .:-=+*#%@"
        
        # Current image data
        self.original_image = None
        self.ascii_text = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="ASCII Painter", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # File selection button
        self.select_btn = ttk.Button(control_frame, text="Select Image", 
                                    command=self.select_image)
        self.select_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Width setting
        ttk.Label(control_frame, text="ASCII Width:").grid(row=0, column=1, padx=(0, 5))
        self.width_var = tk.StringVar(value="80")
        width_spinbox = ttk.Spinbox(control_frame, from_=20, to=200, 
                                   textvariable=self.width_var, width=8)
        width_spinbox.grid(row=0, column=2, padx=(0, 10))
        
        # Convert button
        self.convert_btn = ttk.Button(control_frame, text="Convert to ASCII", 
                                     command=self.convert_to_ascii, state='disabled')
        self.convert_btn.grid(row=0, column=3, padx=(0, 10))
        
        # Save and copy buttons
        self.save_btn = ttk.Button(control_frame, text="Save ASCII", 
                                  command=self.save_ascii, state='disabled')
        self.save_btn.grid(row=0, column=4, padx=(0, 10))
        
        self.copy_btn = ttk.Button(control_frame, text="Copy to Clipboard", 
                                  command=self.copy_to_clipboard, state='disabled')
        self.copy_btn.grid(row=0, column=5)
        
        # Image display frame (left side)
        image_frame = ttk.LabelFrame(main_frame, text="Original Image", padding="10")
        image_frame.grid(row=1, column=0, columnspan=1, sticky=(tk.W, tk.E, tk.N, tk.S), 
                        padx=(0, 5))
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
        ascii_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                        padx=(5, 0))
        ascii_frame.columnconfigure(0, weight=1)
        ascii_frame.rowconfigure(0, weight=1)
        
        # ASCII text display
        self.ascii_display = scrolledtext.ScrolledText(ascii_frame, 
                                                      font=('Courier', 8),
                                                      wrap=tk.NONE,
                                                      state='disabled')
        self.ascii_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
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
        
        # Enable convert button
        self.convert_btn.config(state='normal')
    
    def display_image(self):
        """Display the original image in the canvas"""
        if not self.original_image:
            return
        
        # Calculate display size (max 400x400 for preview)
        display_image = self.original_image.copy()
        display_image.thumbnail((400, 400), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.photo_image = ImageTk.PhotoImage(display_image)
        
        # Clear canvas and add image
        self.image_canvas.delete("all")
        self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        
        # Update scroll region
        self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
    
    def convert_to_ascii(self):
        """Convert the image to ASCII art"""
        if not self.original_image:
            return
        
        try:
            width = int(self.width_var.get())
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
            messagebox.showerror("Error", f"Failed to convert image: {str(e)}")
    
    def image_to_ascii(self, image, width=80):
        """Convert PIL Image to ASCII art"""
        # Calculate height to maintain aspect ratio
        aspect_ratio = image.height / image.width
        height = int(width * aspect_ratio * 0.55)  # 0.55 to compensate for character height
        
        # Resize image
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Convert to grayscale
        grayscale = ImageOps.grayscale(resized)
        
        # Convert to ASCII
        ascii_lines = []
        for y in range(height):
            line = ""
            for x in range(width):
                pixel_value = grayscale.getpixel((x, y))
                # Map pixel value (0-255) to ASCII character index (invert for correct brightness)
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

def main():
    root = tk.Tk()
    app = ASCIIPainter(root)
    root.mainloop()

if __name__ == "__main__":
    main()