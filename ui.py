#!/usr/bin/env python
from time import sleep
import threading
import socket

from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout

HOST = "127.0.0.1"
PORT = 8888

right_buffer = Buffer()

log = BufferControl(buffer=right_buffer)

def on_text_input(buffer: Buffer):
    right_buffer.text += "cmd"
    return True

left_buffer = Buffer(
    multiline=False,
    accept_handler=on_text_input,
)

left_window = Window(BufferControl(buffer=left_buffer))
right_window = Window(log)


body = VSplit(
    [
        left_window,
        Window(width=1, char="/", style="class:line"),
        right_window,
    ]
)

def get_titlebar_text():
    return [
        ("class:title", "gba controller"),
    ]


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

kb = KeyBindings()
def recv():
    # i = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            if application.die == True:
                break

            try:
                data = str(s.recv(1024))

                if not data:
                    break

                if data != "":
                    right_buffer.text += str(data)
                    right_buffer.text += "\n"

                log.move_cursor_down()

                try:
                    s.sendall("alive?".encode())
                except:
                    break

                sleep(0.2) # every 200ms

            except ConnectionResetError:
                break

    application.die = True

t = threading.Thread(target=recv, args=())

@kb.add("c-c", eager=True)
@kb.add("c-q", eager=True)
def bye(event):
    event.app.exit()
    event.app.die = True

application = Application(
    layout=Layout(root_container, focused_element=left_window),
    key_bindings=kb,
    mouse_support=True,
    full_screen=True,
)
application.die = False


def run():
    t.start()
    application.run()

if __name__ == "__main__":
    run()
