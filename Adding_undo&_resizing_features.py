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

    def create_ui(self):
     #Creating and configure canvas for the fixed size
        self.canvas = tk.Canvas(self.root, bg="gray", width=600, height=400)
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

##Putting the limit of the resize button
        self.resize_slider = tk.Scale(btn_frame, from_=10, to=200, orient="horizontal", command=self.resize_image)
        self.resize_slider.set(100)
        self.resize_slider.grid(row=0, column=3, padx=5)


#Createing a Save button for save the resize image
        save_btn = tk.Button(btn_frame, text="Save", command=self.save_image)
        save_btn.grid(row=0, column=6, padx=5)
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
        self.save_to_history()
        self.display_image(self.image)

##Using slider for resizing the image
    def resize_image(self, scale_value):
        if self.image is not None:
            scale = int(scale_value) / 50
            new_size = (int(self.original_image.shape[1] * scale), int(self.original_image.shape[0] * scale))
            self.image = cv2.resize(self.original_image, new_size, interpolation=cv2.INTER_AREA)
            self.save_to_history()
            self.display_image(self.image)


    def save_to_history(self):
        self.history.append(self.image.copy())

#Setting an undo button so that we can go back to and cancel the changes we made
    def undo(self):
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.image = self.history[-1].copy()
            self.display_image(self.image)


#Save the edited image in different name in your device
    def save_image(self):
        """Save the modified image"""
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
