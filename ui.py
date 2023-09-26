#!/usr/bin/env python
from time import sleep
import threading
import socket

import tkinter as tk
from tkinter import ttk

from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout

HOST = "127.0.0.1"
PORT = 8888

class GBAController:
    def __init__(self):
        self.right_buffer = Buffer()
        self.left_buffer = Buffer(
            multiline=False,
            accept_handler=self.on_text_input,
        )

        self.log = BufferControl(buffer=self.left_buffer)

        self.application = self.setup_application()
        self.thread = threading.Thread(target=self.recv, args=())

        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = None

    def on_text_input(self, buffer):
        cmd = ""

        if self.left_buffer.text == "start":
            cmd = "cmd start"
        elif self.left_buffer.text == "stop":
            cmd = "cmd stop"

        if cmd != "":
            self.right_buffer.text += cmd
            self.right_buffer.text += "\n"

        self.left_buffer.text = ""
        return True

    def setup_application(self):
        right_window = Window(BufferControl(buffer=self.right_buffer))

        body = VSplit(
            [
                Window(self.log),
                Window(width=1, char="/", style="class:line"),
                right_window,
            ]
        )

        def get_titlebar_text():
            return [("class:title", "gba controller")]

        root_container = HSplit(
            [
                Window(
                    height=1,
                    content=FormattedTextControl(get_titlebar_text),
                    align=WindowAlign.CENTER,
                ),
                Window(height=1, char="-", style="class:line"),
                body,
            ]
        )



        application = Application(
            layout=Layout(root_container, focused_element=body.children[0]),
            key_bindings=kb,
            mouse_support=True,
            full_screen=True,
        )
        application.die = False
        return application

    def recv(self):
        # self.sock.connect((host, port))
        while True:
            # if self.application.die == True:
                # break

            self.right_buffer.text += "test\n"

            data = str(s.recv(1024))

            if not data:
                break

            # output the data to the right buffer
            if data != "":
                self.right_buffer.text += str(data)
                self.right_buffer.text += "\n"

            self.log.move_cursor_down()

            try:
                s.sendall("alive?".encode())
            except:
                break

            sleep(0.2)  # every 200ms

        self.application.die = True

    def run(self):
        self.thread.start()
        self.application.run()


class MyPromptSession(PromptSession):
    def _create_layout(self):
        custom_buffer = Buffer()
        custom_window = Window(BufferControl(buffer=custom_buffer))
        layout = super()._create_layout()
        main_window = layout.container
        return Layout(
            HSplit(children=[main_window, custom_window], # <-- I can't use VSplit here :(
                padding_char='*',
                padding=1,
            ), 
            main_window
)

kb = KeyBindings()

@kb.add("c-c", eager=True)
@kb.add("c-q", eager=True)
def bye(event):
    event.app.exit()
    # event.app.die = True

class Aplicacion(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.etiqueta_temp_celsius = ttk.Label(
            parent, text="Temperatura en ºC:")
        self.etiqueta_temp_celsius.place(x=20, y=20)

# if __name__ == "__main__":
#
#     ventana = tk.Tk()
#     ventana.title("tensorgba")
#     ventana.config(width=400, height=300)
#     app = Aplicacion(ventana)
#     ventana.mainloop()


import tkinter as tk
from tkinter import ttk
import asyncio

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Subwindow Example")
        
        self.create_widgets()
        
        # Simulated async socket message reception
        self.socket_messages = asyncio.Queue()
        # self.loop = asyncio.get_event_loop()
        # self.loop.create_task(self.receive_messages())

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

            data = str(self.sock.recv(1024))
            if not data:
                continue

            if data != "":
                self.log_text.insert(tk.END, data + "\n")
                self.log_text.see(tk.END)

            try:
                self.sock.sendall("alive?".encode())
            except:
                break

    def run(self):
        self.thread.start()
        self.root.mainloop()

def main():
    root = tk.Tk()
    app = MyApp(root)
    app.run()

if __name__ == "__main__":
    main()


