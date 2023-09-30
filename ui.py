#!/usr/bin/env python
import os
import threading
import socket
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkmb
import csv
import time
import pathlib
from PIL import ImageTk, Image

HOST = "127.0.0.1"
PORT = 8888

class Vizualizer(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent.tabs)

        self.shouldexit = False

        self.path = parent.path

        self.runvideo = False

        flist = [ f.path for f in os.scandir(self.path) if f.is_dir() ]
        self.options = {}

        for folder in flist:
            name = pathlib.PurePath(folder).name
            self.options[name] = folder

        self.create_widgets()

        self.frame = 0
        self.csv = None
        self.file = None

        self.thread = threading.Thread(target=self.video, args=())

    def create_widgets(self):
        self.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.playpause_btn = ttk.Button(self.left_frame, text="refresh", command=self.refresh)
        self.playpause_btn.pack(pady=10)

        self.selected = tk.StringVar()
        self.selected.trace('w', self.on_folder_change)

        self.opts_menu = ttk.Combobox(self.left_frame, state="readonly", values= list(self.options.keys()), textvariable=self.selected )
        self.opts_menu.pack(pady=10)

        self.playpause_btn = ttk.Button(self.left_frame, text="play", command=self.playpause)
        self.playpause_btn.pack(pady=10)
        self.playpause_btn["state"] = "disabled"

        self.reset_btn = ttk.Button(self.left_frame, text="reset", command=self.reset)
        self.reset_btn.pack(pady=10)
        self.reset_btn["state"] = "disabled"

        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.img = ttk.Label(self.right_frame)
        self.img.pack(fill=tk.BOTH, expand=True)
    
    def on_folder_change(self, *args):
        folder = self.selected.get()

        self.runvideo = False
        self.playpause_btn.config(text = "play")
        self.img.config(image='')

        if folder == "":
            self.playpause_btn["state"] = "disabled"
            self.reset_btn["state"] = "disabled"
            return
        else:
            self.playpause_btn["state"] = "normal"
            self.reset_btn["state"] = "normal"

        self.frame = 0

    def refresh(self):
        flist = [ f.path for f in os.scandir(self.path) if f.is_dir() ]
        self.options = {}

        for folder in flist:
            name = pathlib.PurePath(folder).name
            self.options[name] = folder
        self.opts_menu["values"] = list(self.options.keys())

    def video(self):
        while True:
            if self.shouldexit:
                break

            # only run if unpaused
            if self.runvideo:

                row = self.csv[ self.frame ] 

                # ignore header row
                while row[0] == "timestamp":
                    self.frame += 1
                    row = self.csv[ self.frame ] 

                # open image using collumn 0 from csv
                frame_path = self.selected_path + "/pics/" + self.csv[self.frame][0] + ".png"
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

                time.sleep(0.1)

    def reset(self):
        self.frame = 0

    def playpause(self):

        self.selected_path = self.path + "/" + self.selected.get()

        if self.runvideo:
            self.playpause_btn.config(text = "play")
        else:
            self.file = open(self.selected_path + "/info.csv", 'r', newline='')
            self.csv = list(csv.reader(self.file))
            self.playpause_btn.config(text = "pause")

        self.runvideo = not self.runvideo

class GBARecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("GBA Recorder")

        self.shouldexit = False
        self.startstop = False
        self.changing = False
        
        self.thread = threading.Thread(target=self.recv, args=())

        self.path = os.getcwd() + "/data"

        self.csv_filename= "info.csv"

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))

            self.sock.sendall( ("cmd set root '" + self.path + "'").encode("ascii") )
        except:
            self.sock = None

        self.create_widgets()

    def pausetoggle(self):

        if self.startstop:
            self.changing = True
            self.startstopbtn.config(text = "start")
            self.currtxt["state"] = "normal"

            self.file.close()

            self.sock.sendall( bytes("cmd stop", 'ascii') )

        else:
            self.startstopbtn.config(text = "stop")
            self.currtxt["state"] = "disabled"

            fpath = self.path + '/' + self.currtxt_val.get()
            fppath = self.path + '/' + self.currtxt_val.get() + "/pics"

            if not os.path.exists(fpath):
                os.makedirs(fpath)
                os.makedirs(fppath)

            if not os.path.exists(fppath):
                os.makedirs(fppath)

            self.file = open(self.path + '/' + self.currtxt_val.get() + '/' + self.csv_filename, 'a+', newline='')
            self.csv = csv.writer(self.file)

            self.changing = False

            self.sock.sendall( bytes("cmd set curr '" + self.currtxt_val.get() + "'", 'ascii') )

            self.sock.sendall( bytes("cmd start", 'ascii') )

        self.startstop = not self.startstop

    def reconnect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))

            self.connbtn["state"] = "disabled"
            self.sock.sendall( ("cmd set root '" + self.path + "'").encode("ascii") )
        except:
            self.connbtn["state"] = "normal"
            self.sock = None

    def create_widgets(self):
        self.tabs = ttk.Notebook(self.root)

        self.currtxt_val = tk.StringVar()
        self.currtxt_val.trace("w", self.changecurr)
        
        # recording frame
        self.rec_frame = ttk.Frame(self.tabs)
        self.rec_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.rec_frame)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.currtxt = tk.Entry(self.left_frame, textvariable=self.currtxt_val)
        self.currtxt.pack(pady=10)

        self.startstopbtn = ttk.Button(self.left_frame, text="start", command=self.pausetoggle)
        self.startstopbtn.pack(pady=10)
        self.startstopbtn["state"] = "disabled"

        self.connbtn = ttk.Button(self.left_frame, text="connect", command=self.reconnect)
        self.connbtn.pack(pady=10)
        if self.sock == None:
            self.connbtn["state"] = "normal"
        else:
            self.connbtn["state"] = "disabled"

        self.right_frame = ttk.Frame(self.rec_frame)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(self.right_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # visualizing frame
        self.viz_frame = Vizualizer(self)

        self.tabs.add(self.rec_frame, text='record')
        self.tabs.add(self.viz_frame, text='visualize')

        self.tabs.pack(expand = 1, fill = "both")

    def changecurr(self, *args):
        if self.currtxt_val.get() != "":
            self.startstopbtn["state"] = "normal"
        else:
            self.startstopbtn["state"] = "disabled"

    def recv(self):
        while True:
            if self.shouldexit:
                break

            if self.sock == None or self.changing:
                continue

            try:
                data = self.sock.recv(1024)
            except:
                self.connbtn["state"] = "normal"
                self.sock = None
                continue

            data = data.decode('UTF-8')
            data = data.split("<->")

            controller = data[0]
            try:
                controller = int(controller)
            except:
                self.connbtn["state"] = "normal"
                self.sock = None
                continue

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
                self.connbtn["state"] = "normal"
                self.sock = None
                continue

            row = [timestamp, 0, 0, 0, 0, 0]

            if data != "":
                self.log_text.insert(tk.END, timestamp)

                for idx, btn in enumerate(buttons):
                    if controller & btn:
                        row[idx + 1] = 1

                if self.sock == None or self.changing:
                    continue

                self.csv.writerow(row)

                self.log_text.insert(tk.END, "\n")
                self.log_text.see(tk.END)

    def exit(self):
        self.shouldexit = True
        self.viz_frame.shouldexit = True


    def run(self):
        self.thread.start()
        self.viz_frame.thread.start()
        self.root.mainloop()

        self.exit()

def main():
    root = tk.Tk()
    app = GBARecorder(root)
    app.run()

if __name__ == "__main__":
    main()
