#!/usr/bin/env python
import threading
import socket
import tkinter as tk
from tkinter import ttk
import csv
import time
from PIL import ImageTk, Image

HOST = "127.0.0.1"
PORT = 8888

class Vizualizer(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent.tabs)

        self.path = parent.path

        self.runvideo = False
        self.create_widgets()

        self.frame = 0
        self.csv = None
        self.file = None

        self.thread = threading.Thread(target=self.video, args=())

    def create_widgets(self):
        self.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.playpause_btn = ttk.Button(self.left_frame, text="play", command=self.playpause)
        self.playpause_btn.pack(pady=10)

        self.reset_btn = ttk.Button(self.left_frame, text="reset", command=self.reset)
        self.reset_btn.pack(pady=10)

        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)


        self.img = ttk.Label(self.right_frame)
        self.img.pack(fill=tk.BOTH, expand=True)

    def video(self):
        while True:
            # only run if unpaused
            if self.runvideo:

                row = self.csv[ self.frame ] 

                # ignore header row
                while row[0] == "timestamp":
                    self.frame += 1
                    row = self.csv[ self.frame ] 

                # open image using collumn 0 from csv
                frame_path = "pics/" + self.csv[self.frame][0] + ".png"
                frame_img = Image.open(frame_path)
                frame_img = frame_img.resize(( frame_img.size[0]*2 , frame_img.size[1]*2), Image.LANCZOS)

                frame_widget = ImageTk.PhotoImage(frame_img)

                # add image and center it
                self.img.config(image=frame_widget)
                self.img.place(relx=0.5, rely=0.5, anchor="c")

                # go to next frame
                self.frame += 1
                
                # loop when data ends
                try:
                    self.csv[ self.frame ] 
                except IndexError:
                    self.frame = 0

                time.sleep(0.2)

    def reset(self):
        self.frame = 0

    def playpause(self):

        if self.runvideo:
            self.playpause_btn.config(text = "play")
        else:
            self.file = open(self.path, 'r', newline='')
            self.csv = list(csv.reader(self.file))
            self.playpause_btn.config(text = "pause")

        self.runvideo = not self.runvideo

class GBARecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("GBA Recorder")
        
        self.thread = threading.Thread(target=self.recv, args=())

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
        except:
            self.sock

        self.path = "data.csv"

        self.file = open(self.path, 'a', newline='')
        self.csv = csv.writer(self.file)

        # write header
        header = ["timestamp", "a", "b", "right", "left", "rb"]
        self.csv.writerow(header)

        self.create_widgets()
        
    def start(self):
        self.file = open('data.csv', 'a', newline='')
        self.csv = csv.writer(self.file)
        self.sock.sendall( bytes("cmd start", 'ascii') )

    def stop(self):
        self.file.close()
        self.sock.sendall( bytes("cmd stop", 'ascii') )

    def create_widgets(self):
        self.tabs = ttk.Notebook(self.root)
        
        # recording frame
        self.rec_frame = ttk.Frame(self.tabs)
        self.rec_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.rec_frame)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.button1 = ttk.Button(self.left_frame, text="start", command=self.start)
        self.button1.pack(pady=10)

        self.button2 = ttk.Button(self.left_frame, text="stop", command=self.stop)
        self.button2.pack(pady=10)

        self.right_frame = ttk.Frame(self.rec_frame)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(self.right_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # visualizing frame
        self.viz_frame = Vizualizer(self)

        self.tabs.add(self.rec_frame, text='record')
        self.tabs.add(self.viz_frame, text='visualize')

        self.tabs.pack(expand = 1, fill = "both")

    def recv(self):
        while True:

            data = self.sock.recv(1024)
            if not data:
                continue

            data = data.decode('UTF-8')
            data = data.split("<->")

            controller = data[0]
            controller = int(controller)

            BUTTON_A = 1 << 0
            BUTTON_B = 1 << 1
            BUTTON_RIGHT = 1 << 4
            BUTTON_LEFT = 1 << 5
            BUTTON_RB = 1 << 8

            buttons = [BUTTON_A, BUTTON_B, BUTTON_RIGHT, BUTTON_LEFT, BUTTON_RB]

            timestamp = data[1]

            try:
                self.sock.sendall("alive?".encode())
            except:
                break

            row = [timestamp, 0, 0, 0, 0, 0]

            if data != "":
                self.log_text.insert(tk.END, timestamp)

                for idx, btn in enumerate(buttons):
                    if controller & btn:
                        row[idx + 1] = 1

                self.csv.writerow(row)

                # if controller & BUTTON_A:
                #     self.log_text.insert(tk.END, "BUTTON A ")
                # if controller & BUTTON_B:
                #     self.log_text.insert(tk.END, "BUTTON B ")
                # if controller & BUTTON_RIGHT:
                #     self.log_text.insert(tk.END, "BUTTON RIGHT ")
                # if controller & BUTTON_LEFT:
                #     self.log_text.insert(tk.END, "BUTTON LEFT ")
                # if controller & BUTTON_RB:
                #     self.log_text.insert(tk.END, "RIGHT BUMPER")

                self.log_text.insert(tk.END, "\n")
                self.log_text.see(tk.END)

    def run(self):
        self.thread.start()
        self.viz_frame.thread.start()
        self.root.mainloop()

def main():
    root = tk.Tk()
    app = GBARecorder(root)
    app.run()

if __name__ == "__main__":
    main()
