import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import cv2

class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        
        # Frame for buttons and options
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        self.image_label = tk.Label(root)
        self.image_label.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # Variables for width and height
        self.width_var = tk.StringVar(value="0")
        self.height_var = tk.StringVar(value="0")
        
        self.original_image = None
        self.current_image = None
        
        self.create_widgets(control_frame)
        
        # Variable to store current color mode
        self.current_color_mode = "RGB"
    
    def create_widgets(self, control_frame):
        # Buttons for loading and capturing images
        load_btn = tk.Button(control_frame, text="Load Image", command=self.load_image)
        load_btn.grid(row=0, column=0, padx=5, pady=5)
        
        capture_btn = tk.Button(control_frame, text="Capture Image", command=self.capture_image)
        capture_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Dropdown for selecting color channel
        channel_label = tk.Label(control_frame, text="Select Color Channel:")
        channel_label.grid(row=0, column=2, padx=5, pady=5)
        
        self.channel_var = tk.StringVar(value="RGB")
        channel_options = ttk.Combobox(control_frame, textvariable=self.channel_var, values=("Red", "Green", "Blue", "RGB"), state="readonly")
        channel_options.grid(row=0, column=3, padx=5, pady=5)
        channel_options.current(3)
        
        apply_channel_btn = tk.Button(control_frame, text="Apply Channel", command=self.apply_color_channel)
        apply_channel_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # Input for resizing the image
        resize_label = tk.Label(control_frame, text="Resize Image:")
        resize_label.grid(row=0, column=5, padx=5, pady=5)
        
        width_entry = tk.Entry(control_frame, textvariable=self.width_var)
        width_entry.grid(row=0, column=6, padx=5, pady=5)
        
        height_entry = tk.Entry(control_frame, textvariable=self.height_var)
        height_entry.grid(row=0, column=7, padx=5, pady=5)
        
        resize_btn = tk.Button(control_frame, text="Resize Image", command=self.resize_image)
        resize_btn.grid(row=0, column=8, padx=5, pady=5)
        
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg")])
        if file_path:
            self.original_image = Image.open(file_path)
            
            # Check if image has alpha channel (transparency)
            if self.original_image.mode == "RGBA":
                # Create a white background image
                white_background = Image.new("RGBA", self.original_image.size, (255, 255, 255, 255))
                self.original_image = Image.alpha_composite(white_background, self.original_image).convert("RGB")
            
            self.current_image = self.original_image.copy()
            self.display_image(self.current_image)
            
            # Update width and height variables with initial image size
            self.width_var.set(str(self.current_image.width))
            self.height_var.set(str(self.current_image.height))
            
            # Reset color mode to RGB
            self.current_color_mode = "RGB"
            self.channel_var.set("RGB")  # Update combobox selection
    
    def capture_image(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot open webcam")
            return
        ret, frame = cap.read()
        cap.release()
        if ret:
            self.original_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.current_image = self.original_image.copy()
            self.display_image(self.current_image)
            
            # Update width and height variables with initial image size
            self.width_var.set(str(self.current_image.width))
            self.height_var.set(str(self.current_image.height))
            
            # Reset color mode to RGB
            self.current_color_mode = "RGB"
            self.channel_var.set("RGB")  # Update combobox selection
    
    def display_image(self, image):
        self.tk_image = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.tk_image)
    
    def apply_color_channel(self):
        if not self.original_image:
            messagebox.showerror("Error", "No image loaded")
            return
        
        channel = self.channel_var.get()
        
        # Always use original image to apply color channels
        self.current_image = self.original_image.copy()
        
        # Split the image into channels
        r, g, b = self.current_image.split()

        if channel == "Red":
            self.current_image = Image.merge("RGB", (r, Image.new("L", r.size), Image.new("L", r.size)))
        elif channel == "Green":
            self.current_image = Image.merge("RGB", (Image.new("L", g.size), g, Image.new("L", g.size)))
        elif channel == "Blue":
            self.current_image = Image.merge("RGB", (Image.new("L", b.size), Image.new("L", b.size), b))
        else:
            self.current_image = self.original_image.convert("RGB")
        
        self.display_image(self.current_image)
        
        # Update current color mode
        self.current_color_mode = channel
    
    def resize_image(self):
        if not self.original_image:
            messagebox.showerror("Error", "No image loaded")
            return
        
        try:
            new_width = int(self.width_var.get())
            new_height = int(self.height_var.get())
            
            if new_width <= 0 or new_height <= 0:
                messagebox.showerror("Error", "Width and height must be greater than 0")
                return

            self.current_image = self.original_image.resize((new_width, new_height), Image.BILINEAR)
            self.display_image(self.current_image)
        except ValueError:
            messagebox.showerror("Error", "Invalid width or height")
            

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()
