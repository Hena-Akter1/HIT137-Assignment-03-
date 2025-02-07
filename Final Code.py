import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance

##Creating the class and setting the title of the application
class ImageEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assignment 3 - Image Editor by Group 8")
        self.geometry("600x400")

        #Setting the Image variables
        self.original_image = None
        self.display_image = None
        self.image_path = None
        self.crop_window = None
        self.cropped_image_original = None
        self.crop_coords = None
        self.undo_stack = []
        self.redo_stack = []
##for editing the image like brightness, grayscale, rotation and resize
        self.edit_params = {
            'brightness': 1.0,
            'resize_factor': 1.0,
            'grayscale': False,
            'rotation': 0,
            'undo': False,
            'redo': False,
        }

        #Setup the main canvas
        self.canvas = tk.Canvas(self, bg='lavender', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        #Setup the control Frame
        control_frame = tk.Frame(self, bg='red')
        control_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)

        #Creating function for Load Button
        self.load_btn = tk.Button(control_frame, text="📁 Load (Ctrl+O)", 
                                command=self.load_image, bg='black', fg='white')
        self.load_btn.pack(side=tk.LEFT, padx=5)

        #Creating function for crop Button
        self.crop_btn = tk.Button(control_frame, text="🌾 Crop (Ctrl+C)", 
                                command=self.open_crop_editor, state=tk.DISABLED)
        self.crop_btn.pack(side=tk.LEFT, padx=5)


        #For binding keyboard shortcuts
        self.bind('<Control-o>', lambda e: self.load_image())
        self.bind('<Control-c>', lambda e: self.open_crop_editor())
        self.bind('<Control-z>', lambda e: self.undo_image())
        self.bind('<Control-y>', lambda e: self.redo_image())
        self.bind('<Control-s>', lambda e: self.save_image())


        #Cropping variables sothat we can crop the original image
        self.rect = None
        self.start_x = self.start_y = 0
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

##Function for loading the image
    def load_image(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not file_path:
            return

        try:
            self.original_image = Image.open(file_path)
            self.image_path = file_path
            self.show_image()
            self.crop_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")

##Function for displaying the loaded image
    def show_image(self):
        if not self.original_image:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img = self.original_image.copy()
        
        ratio = min(canvas_width/img.width, canvas_height/img.height)
        new_size = (int(img.width*ratio), int(img.height*ratio))
        img = img.resize(new_size, Image.LANCZOS)
        
        self.display_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width//2, canvas_height//2,
                               anchor=tk.CENTER, image=self.display_image)

##Function to crop the image
    def on_mouse_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y,
                                                self.start_x, self.start_y,
                                                outline='orange', width=2)


##Setting the crop area sothat we can drag the mouse to crop the image
    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

##Function to release the mouse button and get the coordinates of the cropped image
    def on_mouse_release(self, event):
        if not self.original_image:
            return

        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        self.crop_coords = (
            min(x1, x2), min(y1, y2),
            max(x1, x2), max(y1, y2)
        )

    def open_crop_editor(self, event=None):
        if not self.crop_coords or not self.original_image:
            messagebox.showwarning("Warning", "Please select a crop area first!")
            return

        # Convert to original image coordinates
        img_width, img_height = self.original_image.size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        scale_x = img_width / canvas_width
        scale_y = img_height / canvas_height

   ##Setting the actual coordinates of the cropped image     
        actual_coords = (
            int(self.crop_coords[0] * scale_x),
            int(self.crop_coords[1] * scale_y),
            int(self.crop_coords[2] * scale_x),
            int(self.crop_coords[3] * scale_y)
        )

        try:
            self.cropped_image_original = self.original_image.crop(actual_coords)
            self.open_editor_window()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid selection:\n{str(e)}")

##Function to open the editor window
    def open_editor_window(self):
        if self.crop_window:
            self.crop_window.destroy()

        self.crop_window = tk.Toplevel(self)
        self.crop_window.title("Image Editor - Cropped")
        self.crop_window.geometry("600x400")
        
        # Add keyboard shortcuts for editor window
        self.crop_window.bind('<Control-s>', lambda e: self.save_image())
        self.crop_window.bind('<Control-r>', lambda e: self.rotate_image())
        self.crop_window.bind('<Control-g>', lambda e: self.toggle_grayscale())
        self.crop_window.bind('<Control-z>', lambda e: self.undo_image())
        self.crop_window.bind('<Control-y>', lambda e: self.redo_image())

        main_frame = tk.Frame(self.crop_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Display the image in a scrollable canvas
        self.img_canvas = tk.Canvas(main_frame, bg='gray', highlightthickness=0)
        vsb = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.img_canvas.yview)
        hsb = tk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.img_canvas.xview)
        self.img_canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

##Setting the image position in the canvas
        self.img_canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)


        self.img_container = tk.Frame(self.img_canvas)
        self.img_canvas.create_window((0,0), window=self.img_container, anchor=tk.NW)

        # Editor controls
        control_frame = tk.Frame(self.crop_window, bg='black')
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        # Adjusting the brightness control by using the slider
        tk.Label(control_frame, text="Brightness:", bg='black', fg='white').pack(side=tk.LEFT, padx=5)
        self.bright_slider = tk.Scale(control_frame, from_=0.2, to=2.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, command=lambda _: self.apply_edits())
        self.bright_slider.set(1.0)
        self.bright_slider.pack(side=tk.LEFT, padx=5)

        # Resize image control by using the slider
        tk.Label(control_frame, text="Resize:", bg='black', fg='white').pack(side=tk.LEFT, padx=5)
        self.resize_slider = tk.Scale(control_frame, from_=0.5, to=3.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, command=lambda _: self.apply_edits())
        self.resize_slider.set(1.0)
        self.resize_slider.pack(side=tk.LEFT, padx=5)

        # Action buttons with keyboard shortcuts
        btn_frame = tk.Frame(control_frame, bg='black')
        btn_frame.pack(side=tk.RIGHT, padx=10)

        self.grayscale_btn = tk.Button(btn_frame, text="◑ Grayscale (Ctrl+G)", command=self.toggle_grayscale)
        self.grayscale_btn.pack(side=tk.LEFT, padx=2)
        
        self.rotate_btn = tk.Button(btn_frame, text="↻ Rotate (Ctrl+R)", command=self.rotate_image)
        self.rotate_btn.pack(side=tk.LEFT, padx=2)

        self.undo_btn = tk.Button(btn_frame, text="Undo (Ctrl+Z)", command=self.undo_image)
        self.undo_btn.pack(side=tk.LEFT, padx=2)

        self.redo_btn = tk.Button(btn_frame, text="Redo (Ctrl+Y)", command=self.redo_image)
        self.redo_btn.pack(side=tk.LEFT, padx=2)
        
        self.save_btn = tk.Button(btn_frame, text="💾 Save (Ctrl+S)", command=self.save_image)
        self.save_btn.pack(side=tk.LEFT, padx=2)

        self.apply_edits()


##Function for applying the edits
    def apply_edits(self):
        if not self.cropped_image_original:
            return

        try:
            img = self.cropped_image_original.copy()
            
            if self.bright_slider.get() != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(self.bright_slider.get())
            
            resize_factor = self.resize_slider.get()
            if resize_factor != 1.0:
                new_size = (int(img.width * resize_factor), int(img.height * resize_factor))
                img = img.resize(new_size, Image.LANCZOS)
            
            if self.edit_params['grayscale']:
                img = img.convert('L')
            
            if self.edit_params['rotation'] != 0:
                img = img.rotate(self.edit_params['rotation'], expand=True)
            
            self.update_display(img)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply edits:\n{str(e)}")

    def undo_image(self):
        if self.undo_image:
            self.redo_image.append(self.cropped_image_original.copy())
            self.cropped_image_original = self.undo_image.pop()
            self.update_display(self.cropped_image_original)

    def redo_image(self):
        if self.redo_image:
            self.undo_image.append(self.cropped_image_original.copy())
            self.cropped_image_original = self.redo_image.pop()
            self.update_display(self.cropped_image_original)

##Function for updating the display image
    def update_display(self, image):
        for widget in self.img_container.winfo_children():
            widget.destroy()
        
        display_img = ImageTk.PhotoImage(image)
        label = tk.Label(self.img_container, image=display_img)
        label.image = display_img
        label.pack()
        
        self.img_container.update_idletasks()
        self.img_canvas.config(scrollregion=self.img_canvas.bbox(tk.ALL))

##Function for setting the grayscale
    def toggle_grayscale(self):
        self.edit_params['grayscale'] = not self.edit_params['grayscale']
        self.grayscale_btn.config(relief=tk.SUNKEN if self.edit_params['grayscale'] else tk.RAISED)
        self.apply_edits()

##Rotating the image by 90 degrees
    def rotate_image(self):
        self.edit_params['rotation'] += 90
        if self.edit_params['rotation'] >= 360:
            self.edit_params['rotation'] = 0
        self.apply_edits()

##Setting the function for saving the updated image
    def save_image(self, event=None):
        if not self.cropped_image_original:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                img = self.cropped_image_original.copy()
                
                if self.bright_slider.get() != 1.0:
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(self.bright_slider.get())
                
                if self.resize_slider.get() != 1.0:
                    new_size = (int(img.width * self.resize_slider.get()),
                               int(img.height * self.resize_slider.get()))
                    img = img.resize(new_size, Image.LANCZOS)
                
                if self.edit_params['grayscale']:
                    img = img.convert('L')
                
                if self.edit_params['rotation'] != 0:
                    img = img.rotate(self.edit_params['rotation'], expand=True)
                
                img.save(file_path)
                messagebox.showinfo("Success", "Image saved successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")

##Main function to run the application
if __name__ == "__main__":
    app = ImageEditor()
    app.mainloop()
