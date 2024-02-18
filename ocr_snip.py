import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
import tkinter as tk
from PIL import ImageGrab
import pyperclip
from google.cloud import vision
import io
import time
import json
import os


CONFIDENCE_FILTER = 0


def ocr_screenshot(img):
    try:
        client = vision.ImageAnnotatorClient()

        image_bytes = io.BytesIO()
        img.save(image_bytes, format="PNG")
        content = image_bytes.getvalue()

        image = vision.Image(content=content)

        response = client.document_text_detection(
            image=image, image_context={"language_hints": ["jp"]}
        )
        document = response.full_text_annotation

        if response.text_annotations[0].locale == 'en':
            return response.text_annotations[0].description

        blocks = []
        for page in document.pages:
            for block in page.blocks:
                block_info = {}
                top_left_vertex = block.bounding_box.vertices[0]
                top_left = (top_left_vertex.x, top_left_vertex.y)

                bottom_right_vertex = block.bounding_box.vertices[2]
                bottom_right = (bottom_right_vertex.x, bottom_right_vertex.y)

                block_info["bounding_box"] = [top_left, bottom_right]
                block_info["confidence"] = block.confidence
                text_list = []
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        for symbol in word.symbols:
                            text_list.append(symbol.text)
                text = "".join(text_list)
                block_info["text"] = text
                blocks.append(block_info)
        return blocks
    except:
        return ""


class OcrSnip(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setWindowTitle(" ")
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setWindowOpacity(0.3)
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor("black"), 3))
        qp.setBrush(QtGui.QColor(128, 128, 255, 128))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def save_debug(self, img, ocr_data):
        timestamp = str(int(time.time()))
        if not os.path.exists("debug"):
            os.mkdir("debug")
        img.save(f"debug/{timestamp}.jpg")
        with open(f"debug/{timestamp}.json", "w", encoding="utf_8_sig") as f:
            f.write(json.dumps(ocr_data))

    def mouseReleaseEvent(self, event):
        self.close()

        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        ocr_data = ocr_screenshot(img)
        self.save_debug(img, ocr_data)
        if not isinstance(ocr_data, str):
            ocr_text = "\n".join(
                x["text"] for x in ocr_data if x["confidence"] > CONFIDENCE_FILTER
            )
        else:
            ocr_text = ocr_data
        pyperclip.copy(ocr_text)
        print(ocr_text)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = OcrSnip()
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())
