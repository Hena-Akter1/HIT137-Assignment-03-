import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.root.geometry("800x600")

#Keeps the last modified state
        self.image = None
        self.original_image = None
        self.modified_image = None
        self.tk_image = None
        self.history = []
        self.redo_stack = []


        self.create_ui()
        self.bind_shortcuts()

    def create_ui(self):
     #Creating and configure canvas for the fixed size
        self.canvas = tk.Canvas(self.root, bg="lavender", width=600, height=400)
        self.canvas.pack(pady=20)
#creating buttong frames for the buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

#Create a button named Load Image for selecting and upload an image in the app 
        load_btn = tk.Button(btn_frame, text="Load Image", command=self.load_image)
        load_btn.grid(row=0, column=0, padx=5)

##Creating a button for resizing image
        resize_label = tk.Label(btn_frame, text="Resize:")
        resize_label.grid(row=0, column=2, padx=5)
##Creating button for undo the current changes
        button_style = {"padx": 5, "pady": 5}
        undo_btn = tk.Button(btn_frame, text="Undo", command=self.undo, **button_style)
        undo_btn.grid(row=1, column=2, padx=5, pady=5)

##Creating a button for redo the changes
        redo_btn = tk.Button(btn_frame, text="Redo", command=self.redo, **button_style)
        redo_btn.grid(row=1, column=3, padx=5, pady=5)
##Putting the limit of the resize button
        self.resize_slider = tk.Scale(btn_frame, from_=10, to=200, orient="horizontal", command=self.resize_image)
        self.resize_slider.set(100)
        self.resize_slider.grid(row=0, column=3, padx=5)

##Creating a slider for brightness adjustment
        brightness_label = tk.Label(btn_frame, text="Brightness:", **button_style)
        brightness_label.grid(row=1, column=0, padx=5, pady=5)
##Putting the limit of the brightness button
        self.brightness_slider = tk.Scale(btn_frame, from_=-100, to=100, orient="horizontal", command=self.adjust_brightness)
        self.brightness_slider.set(0)
        self.brightness_slider.grid(row=1, column=1, padx=5, pady=5)

##Creating a button for cropping the image
        crop_btn = tk.Button(btn_frame, text="Crop", command=self.start_crop, **button_style)
        crop_btn.grid(row=0, column=1, padx=5, pady=5)

##Button for rotating the image in 90 degree
        rotate_btn = tk.Button(btn_frame, text="Rotate", command=self.rotate_image, **button_style)
        rotate_btn.grid(row=1, column=3, padx=5, pady=5)

##Creating a button for changing the color of image to black and white
        bw_btn = tk.Button(btn_frame, text="B&W", command=self.convert_to_black_and_white, **button_style)
        bw_btn.grid(row=0, column=5, padx=5, pady=5)

##Creating a button for reverting the image to the original state
        revert_btn = tk.Button(btn_frame, text="Revert", command=self.revert_to_original, **button_style)
        revert_btn.grid(row=0, column=6, padx=5, pady=5)

#Createing a Save button for save the resize image
        save_btn = tk.Button(btn_frame, text="Save", command=self.save_image)
        save_btn.grid(row=1, column=4, padx=5)
##Create a bar for showing the status Label      
        self.status_label = tk.Label(self.root, text="Welcome to the Image Editor", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)



##Load an image from file and display it in the Tkinter Canvas
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
        if file_path:
            self.image = cv2.imread(file_path)
            self.original_image = self.image.copy()
            self.modified_image = self.image.copy()
            self.history = [self.image.copy()]
            self.redo_stack.clear()
            self.display_image(self.image)

##Convert and display the image in Tkinter Canvas
    def display_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(300, 200, anchor=tk.CENTER, image=self.tk_image)


        self.canvas.bind("<ButtonPress-1>", self.on_crop_start)
        self.canvas.bind("<B1-Motion>", self.on_crop_draw)
        self.canvas.bind("<ButtonRelease-1>", self.on_crop_end)

    

# Convert Tkinter coordinates to image coordinates
        img_h, img_w, _ = self.image.shape
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        x1 = int((x1 / canvas_w) * img_w)
        y1 = int((y1 / canvas_h) * img_h)
        x2 = int((x2 / canvas_w) * img_w)
        y2 = int((y2 / canvas_h) * img_h)

        self.image = self.image[y1:y2, x1:x2]
        ##Save the image to history, display the image
        self.save_to_history()
        self.display_image(self.image)

##Using slider for resizing the image
    def resize_image(self, scale_value):
        if self.image is not None:
            scale = int(scale_value) / 50
            new_size = (int(self.original_image.shape[1] * scale), int(self.original_image.shape[0] * scale))
            self.image = cv2.resize(self.original_image, new_size, interpolation=cv2.INTER_AREA)
            ##Save the image to history, display the image
            self.save_to_history()
            self.display_image(self.image)

##Set the brightness of the loaded image
    def adjust_brightness(self, value):
        if self.image is not None:
            value = int(value)
            hsv = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            v = cv2.add(v, value)
            v = np.clip(v, 0, 255)
            final_hsv = cv2.merge((h, s, v))
            self.image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
            ##Save the image to history, display the image and show the status
            self.save_to_history()
            self.display_image(self.image)
            self.status_label.config(text="Brightness adjusted")
##Save the image to history
    def save_to_history(self):
        self.history.append(self.image.copy())

#Setting an undo button so that we can go back to and cancel the changes we made
    def undo(self):
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.image = self.history[-1].copy()
            self.display_image(self.image)

##Setting a redo function so that we can redo the undone changes
    def redo(self):
        if self.redo_stack:
            self.image = self.redo_stack.pop()
            ##Save the image to history, display the image and show the status
            self.history.append(self.image.copy())
            self.display_image(self.image)
            self.status_label.config(text="Redo last action")

 ##Setting keyborad shortcuts for the buttons
    def bind_shortcuts(self):
        self.root.bind("<Control-z>", lambda _: self.undo())
        self.root.bind("<Control-y>", lambda _: self.redo())
        self.root.bind("<Control-o>", lambda _: self.load_image())
        self.root.bind("<Control-s>", lambda _: self.save_image())

## We can Enable cropping functionality by capturing mouse clicks and drags 
    def start_crop(self):
        if self.image is None:
            messagebox.showerror("Error", "Load an image first!")
            return

        self.canvas.bind("<ButtonPress-1>", self.on_crop_start)
        self.canvas.bind("<B1-Motion>", self.on_crop_draw)
        self.canvas.bind("<ButtonRelease-1>", self.on_crop_end)
        self.status_label.config(text="Click and drag to select crop area")

  
## For starting the drawing the crop rectangle
    def on_crop_start(self, event):
        self.crop_start_x, self.crop_start_y = event.x, event.y
        self.is_cropping = True
        self.canvas.delete("crop_rect")

##Dynamically draw the cropping rectangle
    def on_crop_draw(self, event):
        if self.is_cropping:
            self.canvas.delete("crop_rect")
            self.canvas.create_rectangle(self.crop_start_x, self.crop_start_y, event.x, event.y,
                                       outline="red", tags="crop_rect")


##Complete cropping and extract the selected region
    def on_crop_end(self, event):
        if not self.is_cropping:
            return

        self.crop_end_x, self.crop_end_y = event.x, event.y
        self.is_cropping = False      

# Get the image dimensions
        img_h, img_w = self.image.shape[:2]
        
        # Calculate scale factors
        display_h = 400  # Canvas height
        display_w = 600  # Canvas width
        
        # Calculate the scaled size of the image so that it fits within the canvas
        scale = min(display_w/img_w, display_h/img_h)
        scaled_w = int(img_w * scale)
        scaled_h = int(img_h * scale)
        
        # Calculate image offset in canvas
        offset_x = (display_w - scaled_w) // 2
        offset_y = (display_h - scaled_h) // 2
        
        # Adjust crop coordinates relative to the image
        x1 = min(self.crop_start_x, self.crop_end_x) - offset_x
        y1 = min(self.crop_start_y, self.crop_end_y) - offset_y
        x2 = max(self.crop_start_x, self.crop_end_x) - offset_x
        y2 = max(self.crop_start_y, self.crop_end_y) - offset_y
        
        # Ensure coordinates are within the scaled image bounds
        x1 = max(0, min(scaled_w, x1))
        y1 = max(0, min(scaled_h, y1))
        x2 = max(0, min(scaled_w, x2))
        y2 = max(0, min(scaled_h, y2))
        
        # Convert to original image coordinates to perform the crop
        x1 = int((x1 / scaled_w) * img_w)
        y1 = int((y1 / scaled_h) * img_h)
        x2 = int((x2 / scaled_w) * img_w)
        y2 = int((y2 / scaled_h) * img_h)
        
        # Check if the crop area is valid or not
        if x1 == x2 or y1 == y2:
            messagebox.showerror("Error", "Invalid crop area!")
            return
        
        # Perform the crop area
        self.image = self.image[y1:y2, x1:x2]
        ##Save the image to history, display the image and show the status
        self.save_to_history()
        self.display_image(self.image)
        self.status_label.config(text="Image cropped")  

##Rotate the image by 90 degrees every time the button is clicked
    def rotate_image(self):
        if self.image is not None:
            self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
            ##Save the image to history, display the image and show the status
            self.save_to_history()
            self.display_image(self.image)
            self.status_label.config(text="Image rotated")

##Convert the image to black and white (grayscale) and display it
    def convert_to_black_and_white(self):
        if self.image is not None:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
            ##Save the image to history, display the image and show the status
            self.save_to_history()
            self.display_image(self.image)
            self.status_label.config(text="Image converted to black & white")


##Revert the image into its original state
    def revert_to_original(self):
        if self.original_image is not None:
            self.image = self.original_image.copy()
            ##Save the image to history, display the image and show the status
            self.save_to_history()
            self.display_image(self.image)
            self.status_label.config(text="Reverted to original image")          


#Save the edited image in different name in your device
    def save_image(self):
        if self.image is None:
            messagebox.showerror("Error", "No image to save!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if file_path:
            cv2.imwrite(file_path, self.image)
            messagebox.showinfo("Success", "Image saved successfully!")

            

##Close the program
if __name__ == "__main__":
    root = tk.Tk()
app = ImageEditorApp(root)
root.mainloop()
