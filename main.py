from pynput.keyboard import GlobalHotKeys
from PyQt5 import QtWidgets
from ocr_snip import OcrSnip
import sys


hotkey = ["<cmd_l>", "<shift>", "w"]
h = None


# The function called when a hotkey is pressed
def snip():
    global app
    print("Snip hotkey pressed")
    app = QtWidgets.QApplication(sys.argv)
    window = OcrSnip()
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    app.exit(app.exec_())
    # state gets frozen during callback function so manually clear to avoid weird inputs
    if h:
        for hk in h._hotkeys:
            hk._state.clear()


if __name__ == "__main__":
    with GlobalHotKeys({"+".join(hotkey): snip}) as h:
        h.join()
