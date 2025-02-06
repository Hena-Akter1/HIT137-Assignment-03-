import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

##creating the Image Editor app
class ImageEditorApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.root.geometry("800x600")

        # Keep the record of the last modify stage                
        self.image = None
        self.original_image = None
        self.modified_image = None 
        self.tk_image = None
	#for history
        self.history = []
	#for redo
        self.redo_stack = []


        self.create_ui()


#Create UI buttons elements
    def create_ui(self):
        ##Create the frame for the buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

        #for loading a image
        load_btn = tk.Button(btn_frame, text="Load Image", command=self.load_image)
        load_btn.grid(row=0, column=0, padx=5)

        #for save the loading or editing image
        save_btn = tk.Button(btn_frame, text="Save", command=self.save_image)
        save_btn.grid(row=0, column=6, padx=5)

        #Create UI canvas element
        self.canvas = tk.Canvas(self.root, bg="gray", width=600, height=400)
        self.canvas.pack(pady=20)


##Setting the program for all types of images so that it can be loaded
    def load_image(self):
        """Load an image from file and display it"""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", ".jpg;.png;*.jpeg")])
        if file_path:
            self.image = cv2.imread(file_path)
            self.original_image = self.image.copy()
            self.modified_image = self.image.copy()
            self.history = [self.image.copy()]
            self.redo_stack.clear()
            self.display_image(self.image)

##Displaying the image file into our program
    def display_image(self, img):
        """Convert and display the image in Tkinter Canvas"""
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(300, 200, anchor=tk.CENTER, image=self.tk_image)




 ## Converting the Tkinter coordinates to the image coordinates
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

#Save the edit history of the image
    def save_to_history(self):
        """Save current image state for undo"""
        self.history.append(self.image.copy())

#Setting an undo button so that we can go back to and cancel the changes we made
    def undo(self):
        """Undo the last change"""
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.image = self.history[-1].copy()
            self.display_image(self.image)


#save the edited image in different name in your device
    def save_image(self):
        """Save the modified image"""
        if self.image is None:
            messagebox.showerror("Error", "No image to save!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", ".png"), ("JPEG files", ".jpg")])
        if file_path:
            cv2.imwrite(file_path, self.image)
            messagebox.showinfo("Success", "Image saved successfully!")

##closing the code
if _name_ == "_main_":
    root = tk.Tk()
    app = ImageEditorApp(root)
root.mainloop()
