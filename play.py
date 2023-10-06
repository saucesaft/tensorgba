#!/usr/bin/env python
import io
import threading
import socket
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

from train import model
from skimage.transform import resize
from skimage.io import imread
import numpy as np
from threading import Thread

HOST = "127.0.0.1"
PORT = 8888

# ImageFile.LOAD_TRUNCATED_IMAGES = True

class GBARecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("GBA Recorder")

        self.shouldexit = False
        self.startstop = False
        
        self.thread = threading.Thread(target=self.recv_frame, args=())

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))

        except:
            self.sock = None

        self.create_widgets()

        self.m = model()
        self.m.load_weights('attempt_repo.h5')

    def reconnect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))

            self.connbtn["state"] = "disabled"
        except:
            self.connbtn["state"] = "normal"
            self.sock = None

    def create_widgets(self):
        self.tabs = ttk.Notebook(self.root)

        # recording frame
        self.rec_frame = ttk.Frame(self.tabs)
        self.rec_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.rec_frame)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.connbtn = ttk.Button(self.left_frame, text="connect", command=self.reconnect)
        self.connbtn.pack(pady=10)
        if self.sock == None:
            self.connbtn["state"] = "normal"
        else:
            self.connbtn["state"] = "disabled"

        self.right_frame = ttk.Frame(self.rec_frame)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.img = ttk.Label(self.right_frame)
        self.img.pack(fill=tk.BOTH, expand=True)

        self.tabs.pack(expand = 1, fill = "both")

    def recv_frame(self):
        while True:
            if self.sock == None:
                continue

            if self.shouldexit:
                break

            data = b''

            while True:
                chunk = self.sock.recv(1024)
                data += chunk

                if b'\x00IEND' in chunk:
                    break
            try:
                
                image = Image.open(io.BytesIO(data))

                img_rgb = image.convert('RGB')

                photo = ImageTk.PhotoImage(image)
                self.img.config(image=photo)
                self.img.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

                img_array = np.array(img_rgb)
                img_array = img_array[30:108, 30:195]
                img_array = resize(img_array, (66, 200, 3))
                img_array = np.expand_dims(img_array, axis=0)

                thread = Thread(target=self.prediction, args=(img_array,))
                thread.start()

            except:
                continue

    def prediction(self, img):
        out = self.m.predict(img, batch_size=1, verbose="0")
        # print( out )
        print( np.where(out > 0.2, 1, 0) )
        print("--------------")

    def exit(self):
        self.shouldexit = True

    def run(self):
        self.thread.start()
        self.root.mainloop()

        self.exit()

def main():

    print('\n --> start <-- \n')

    # # image = imread('data/cheese_2/pics/1696488126_5.png')
    # image = imread('test2.png')
    # image = image[30:108, 30:195]
    # resized_image = resize(image, (66, 200, 3))
    # image_array = np.expand_dims(resized_image, axis=0)
    #
    # out = m.predict(image_array, batch_size=1, verbose="0")
    #
    # print( out )
    # print( np.where(out > 0.2, 1, 0) )
    #
    # return
    root = tk.Tk()
    app = GBARecorder(root)
    app.run()

if __name__ == "__main__":
    main()
