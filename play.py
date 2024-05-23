#!/usr/bin/env python
import threading
import socket
import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image
import cv2

from train import model
import numpy as np
from threading import Thread

HOST = "127.0.0.1"
PORT = 8888

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

        self.mode = 'manual'

        self.create_widgets()

        self.m = model()
        self.m.load_weights('attempt_yuv.h5')

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

        self.modelabel = ttk.Label(self.left_frame, text = "modo: " + self.mode)
        self.modelabel.pack(pady=10)

        self.modebtn = ttk.Button(self.left_frame, text="cambiar modo", command=self.changemode)
        self.modebtn.pack(pady=10)

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
                
                # load photo with opencv
                image_bytes = np.asarray(bytearray(data), dtype="uint8")
                image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # convert to PIL readable format
                image_pil = Image.fromarray(image)
                photo = ImageTk.PhotoImage(image_pil)
                self.img.config(image=photo)
                self.img.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

                # do operations with it and feed it to the CNN
                image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
                image = image[30:108, 30:195]
                image = cv2.resize(image, (200, 66), interpolation=cv2.INTER_LINEAR)
                image = np.expand_dims(image, axis=0)

                thread = Thread(target=self.prediction, args=(image,))
                thread.start()

            except:
                continue

    def changemode(self):
        if self.mode == 'manual':
            self.mode = 'ai'
        else:
            self.mode = 'manual'

        self.modelabel.config(text = "modo: " + self.mode)

    def prediction(self, img):
        if self.mode != 'ai':
            return

        out = self.m.predict(img, batch_size=1, verbose="0")
        out = np.where(out > 0.5, 1, 0)
        out = out[0]

        print(out)

        if self.sock is not None:

            result = 0
            result |= out[0] << 0  # BUTTON_A
            result |= out[1] << 1  # BUTTON_B
            result |= out[2] << 4  # BUTTON_RIGHT
            result |= out[3] << 5  # BUTTON_LEFT
            result |= out[4] << 7  # BUTTON_DOWN
            result |= out[5] << 8  # BUTTON_RB

            self.sock.sendall( str(result).encode() )

    def exit(self):
        self.shouldexit = True

    def run(self):
        self.thread.start()
        self.root.mainloop()

        self.exit()

def main():

    print('\n --> start <-- \n')


    # m = model()
    # m.load_weights('attempt_yuv.h5')
    #
    # image = cv2.imread('test.png')
    # # image = cv2.imread('data/cheese_2/pics/1696488126_5.png')
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    # image = image[30:108, 30:195]
    # image = cv2.resize(image, (200, 66), interpolation=cv2.INTER_LINEAR)
    # image = np.expand_dims(image, axis=0)
    #
    # out = m.predict(image, batch_size=1, verbose="0")
    #
    # print( out )
    # print( np.where(out > 0.5, 1, 0) )
    #
    # return

    root = tk.Tk()
    app = GBARecorder(root)
    app.run()

if __name__ == "__main__":
    main()
