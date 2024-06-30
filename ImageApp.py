import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import cv2

class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработчик изображений")
        
        # Фрейм для кнопок и опций
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        self.image_label = tk.Label(root)
        self.image_label.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # Переменные для ширины и высоты
        self.width_var = tk.StringVar(value="0")
        self.height_var = tk.StringVar(value="0")
        
        self.original_image = None
        self.current_image = None
        
        self.create_widgets(control_frame)
        
        # Переменная для текущего цветового режима
        self.current_color_mode = "RGB"
    
    def create_widgets(self, control_frame):
        
        # Кнопки для загрузки и захвата изображений
        load_btn = tk.Button(control_frame, text="Загрузить изображение", command=self.load_image)
        load_btn.grid(row=0, column=0, padx=5, pady=5)
        
        capture_btn = tk.Button(control_frame, text="Захватить изображение", command=self.capture_image)
        capture_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Выпадающий список для выбора цветового канала
        channel_label = tk.Label(control_frame, text="Выберите цветовой канал:")
        channel_label.grid(row=0, column=2, padx=5, pady=5)
        
        self.channel_var = tk.StringVar(value="RGB")
        channel_options = ttk.Combobox(control_frame, textvariable=self.channel_var, values=("Red", "Green", "Blue", "RGB"), state="readonly")
        channel_options.grid(row=0, column=3, padx=5, pady=5)
        channel_options.current(3)
        
        apply_channel_btn = tk.Button(control_frame, text="Применить канал", command=self.apply_color_channel)
        apply_channel_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # Поля для изменения размера изображения
        resize_label = tk.Label(control_frame, text="Изменить размер:")
        resize_label.grid(row=0, column=5, padx=5, pady=5)
        
        width_entry = tk.Entry(control_frame, textvariable=self.width_var)
        width_entry.grid(row=0, column=6, padx=5, pady=5)
        
        height_entry = tk.Entry(control_frame, textvariable=self.height_var)
        height_entry.grid(row=0, column=7, padx=5, pady=5)
        
        resize_btn = tk.Button(control_frame, text="Изменить размер", command=self.resize_image)
        resize_btn.grid(row=0, column=8, padx=5, pady=5)
        
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png;*.jpg")])
        if file_path:
            self.original_image = Image.open(file_path)
            
            # Проверяем наличие альфа-канала (прозрачности)
            if self.original_image.mode == "RGBA":
                
                # Создаем изображение с белым фоном
                white_background = Image.new("RGBA", self.original_image.size, (255, 255, 255, 255))
                self.original_image = Image.alpha_composite(white_background, self.original_image).convert("RGB")
            
            self.current_image = self.original_image.copy()
            self.display_image(self.current_image)
            
            # Обновляем переменные ширины и высоты исходного размера изображения
            self.width_var.set(str(self.current_image.width))
            self.height_var.set(str(self.current_image.height))
            
            # Сбрасываем цветовой режим на RGB
            self.current_color_mode = "RGB"
            self.channel_var.set("RGB")  # Обновляем выбор в выпадающем списке
    
    def capture_image(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Ошибка", "Невозможно открыть веб-камеру")
            return
        ret, frame = cap.read()
        cap.release()
        if ret:
            self.original_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.current_image = self.original_image.copy()
            self.display_image(self.current_image)
            
            # Обновляем переменные ширины и высоты исходного размера изображения
            self.width_var.set(str(self.current_image.width))
            self.height_var.set(str(self.current_image.height))
            
            # Сбрасываем цветовой режим на RGB
            self.current_color_mode = "RGB"
            self.channel_var.set("RGB")  # Обновляем выбор в выпадающем списке
    
    def display_image(self, image):
        self.tk_image = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.tk_image)
    
    def apply_color_channel(self):
        if not self.original_image:
            messagebox.showerror("Ошибка", "Изображение не загружено")
            return
        
        channel = self.channel_var.get()
        
        # Всегда используем исходное изображение для применения цветовых каналов
        self.current_image = self.original_image.copy()
        
        # Разделяем изображение на каналы
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
        
        # Обновляем текущий цветовой режим
        self.current_color_mode = channel
    
    def resize_image(self):
        if not self.original_image:
            messagebox.showerror("Ошибка", "Изображение не загружено")
            return
        
        try:
            new_width = int(self.width_var.get())
            new_height = int(self.height_var.get())
            
            if new_width <= 0 or new_height <= 0:
                messagebox.showerror("Ошибка", "Ширина и высота должны быть больше 0")
                return

            self.current_image = self.original_image.resize((new_width, new_height), Image.BILINEAR)
            self.display_image(self.current_image)
        except ValueError:
            messagebox.showerror("Ошибка", "Неверная ширина или высота")
            

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()
