#!/usr/bin/env python
import threading
import socket
import tkinter as tk
from tkinter import ttk
import asyncio

HOST = "127.0.0.1"
PORT = 8888

class GBARecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Subwindow Example")
        
        self.create_widgets()
        
        self.thread = threading.Thread(target=self.recv, args=())

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        
    def start(self):
        self.sock.sendall( bytes("cmd start", 'ascii') )

    def stop(self):
        self.sock.sendall( bytes("cmd stop", 'ascii') )

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Subwindow on the left with buttons
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.button1 = ttk.Button(self.left_frame, text="start", command=self.start)
        self.button1.pack(pady=10)

        self.button2 = ttk.Button(self.left_frame, text="stop", command=self.stop)
        self.button2.pack(pady=10)

        # Subwindow on the right with a text log
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(self.right_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        # ... (same as before)

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

            timestamp = data[1]

            try:
                self.sock.sendall("alive?".encode())
            except:
                break

            if data != "":
                self.log_text.insert(tk.END, timestamp)

                if controller & BUTTON_A:
                    self.log_text.insert(tk.END, "BUTTON A ")
                if controller & BUTTON_B:
                    self.log_text.insert(tk.END, "BUTTON B ")
                if controller & BUTTON_RIGHT:
                    self.log_text.insert(tk.END, "BUTTON RIGHT ")
                if controller & BUTTON_LEFT:
                    self.log_text.insert(tk.END, "BUTTON LEFT ")
                if controller & BUTTON_RB:
                    self.log_text.insert(tk.END, "RIGHT BUMPER")

                self.log_text.insert(tk.END, "\n")
                self.log_text.see(tk.END)

    def run(self):
        self.thread.start()
        self.root.mainloop()

def main():
    root = tk.Tk()
    app = GBARecorder(root)
    app.run()

if __name__ == "__main__":
    main()


