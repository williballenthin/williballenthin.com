from __future__ import annotations


### setup: prior to importing textual
import os
# ensure textual/rich recognizes we're in terminal with lots of colors.
os.environ["COLORTERM"] = "truecolor"
os.environ["TERM"] = "xterm-256color"
# set the driver that textual should use: xterm.js defined below.
# this must happen before textual is loaded,
# or we could manipulate textual.constants.DRIVER directly.
os.environ["TEXTUAL_DRIVER"] = "__main__:XtermjsDriver"
### end setup


### hack until https://github.com/Textualize/textual/issues/2468 is addressed
import inspect

def getfile(*args, **kwargs):
    raise TypeError("getfile() is not supported in the browser")

inspect.getfile = getfile
import textual.dom
textual.dom.getfile = getfile
### end hack

import os
import asyncio
from dataclasses import dataclass

import textual
import textual.events
from textual.message import Message
from textual.driver import Driver
from textual.geometry import Size
from textual._xterm_parser import XTermParser

# implicit from pyodide environment
import js
import pyodide.ffi

js.console.log("hello from textual host")


@dataclass
class DataEvent:
    data: str


@dataclass
class ResizeEvent:
    rows: int
    cols: int


# TODO: KeyEvent, ScrollEvent, TitleEvent


@dataclass
class NotifyEvent:
    """application specific event from the JS host application
    
    will be posted to the app as a Notified event.
    """
    data: Any 


# relies on global TERMINAL_Q
# manipulates js.term directly
class XtermjsDriver(Driver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.q = asyncio.Queue()

        # constructing an instance of this class
        # grabs the global message handler.
        # therefore, assumption: there is only XtermjsDriver in use at a time.
        # also note this isn't cleaned up
        js.onmessage = self.onmessage

        self.post_syn()

    async def onmessage(self, msg):
        type = msg.data.type
        if type == "data":
            await self.q.put(DataEvent(data=msg.data.data))
        elif type == "resize":
            await self.q.put(ResizeEvent(rows=msg.data.rows, cols=msg.data.cols))
        elif type == "notify":
            await self.q.put(NotifyEvent(data=msg.data.data))
        else:
            js.console.log("py: unhandled message: ", msg.data.type)

    @property
    def is_headless(self) -> bool:
        return False

    @staticmethod
    def post_data(data):
        """Post data from the WebWorker to the terminal stream."""
        msg = js.Object.fromEntries(
            pyodide.ffi.to_js({
                "type": "data",
                "data": data,
            }))
        js.postMessage(msg)

    @staticmethod
    def post_syn():
        """Make an initial connection from the WebWorker."""
        msg = js.Object.fromEntries(
            pyodide.ffi.to_js({
                "type": "syn",
            }))
        js.postMessage(msg)

    def write(self, data: str) -> None:
        self.post_data(data)

    def _enable_mouse_support(self) -> None:
        """Enable reporting of mouse events."""
        write = self.write
        write("\x1b[?1000h")  # SET_VT200_MOUSE
        write("\x1b[?1003h")  # SET_ANY_EVENT_MOUSE
        write("\x1b[?1015h")  # SET_VT200_HIGHLIGHT_MOUSE
        write("\x1b[?1006h")  # SET_SGR_EXT_MODE_MOUSE

        # Note: E.g. lxterminal understands 1000h, but not the urxvt or sgr
        #       extensions.

    def _enable_bracketed_paste(self) -> None:
        """Enable bracketed paste mode."""
        self.write("\x1b[?2004h")

    def _disable_bracketed_paste(self) -> None:
        """Disable bracketed paste mode."""
        self.write("\x1b[?2004l")

    def _disable_mouse_support(self) -> None:
        """Disable reporting of mouse events."""
        write = self.write
        write("\x1b[?1000l")  #
        write("\x1b[?1003l")  #
        write("\x1b[?1015l")
        write("\x1b[?1006l")

    def _request_terminal_sync_mode_support(self) -> None:
        """Writes an escape sequence to query the terminal support for the sync protocol."""
        # Terminals should ignore this sequence if not supported.
        self.write("\033[?2026$p")

    class Notified(Message):
        def __init__(self, data: Any):
            super().__init__()
            self.data = data

    def start_application_mode(self) -> None:
        """Start application mode."""
        loop = asyncio.get_running_loop()

        async def handle_events() -> None:
            parser = XTermParser(lambda: False, self._debug)

            while True:
                event = await self.q.get()
                if isinstance(event, DataEvent):
                    for ev in parser.feed(event.data):
                        # js.console.log("event1: ", str(ev), repr(ev))
                        self.process_event(ev)
                elif isinstance(event, ResizeEvent):
                    size = Size(event.cols, event.rows)
                    self.process_event(textual.events.Resize(size, size))
                elif isinstance(event, NotifyEvent): 
                    self._app.post_message(self.Notified(event.data))
                else:
                    raise NotImplementedError(event)

        asyncio.run_coroutine_threadsafe(
            handle_events(),
            loop=loop,
        )

        self.write("\x1b[?1049h")  # Alt screen
        self._enable_mouse_support()
        self.write("\x1b[?25l")  # Hide cursor
        self.write("\033[?1003h\n")  # report all mouse events
        self._request_terminal_sync_mode_support()
        self._enable_bracketed_paste()

    def stop_application_mode(self) -> None:
        """Stop application mode, restore state."""
        self._disable_bracketed_paste()
        self.disable_input()

        # Alt screen false, show cursor
        self.write("\x1b[?1049l" + "\x1b[?25h")

    def disable_input(self) -> None:
        """Disable further input."""
