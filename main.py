from pynput.keyboard import GlobalHotKeys
from PyQt5 import QtWidgets
from ocr_snip import OcrSnip
import sys
import threading


hotkey = ["<cmd_l>", "<shift>", "w"]
h = None
app = None
window = None


def open_snip():
    global app
    global window
    app = QtWidgets.QApplication(sys.argv)
    window = OcrSnip()
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    app.exit(app.exec_())
    app = None
    window = None


def reset_hotkeys():
    global h
    # state gets frozen during callback function so manually clear to avoid weird inputs
    if h:
        for hk in h._hotkeys:
            hk._state.clear()


# The function called when a hotkey is pressed
def snip():
    global app
    if not app:
        th = threading.Thread(target=open_snip)
        th.start()
    reset_hotkeys()


def quit():
    global window
    if window:
        window.close()
    reset_hotkeys()


if __name__ == "__main__":
    # <esc> key requires a hack to pynput
    # see https://github.com/moses-palmer/pynput/pull/466
    with GlobalHotKeys({"+".join(hotkey): snip, "<esc>": quit}) as h:
        h.join()
