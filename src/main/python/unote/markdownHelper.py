from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QRectF, QEvent, QThread, pyqtSignal, pyqtSlot,QObject, QPoint
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QWidget

import markups

testHTML = '''# Title

## Subtitle

some text

- a
- listing

---

and more text'''

class markdownHelper():
    def __init__(self):

        self.markup = markups.MarkdownMarkup()

        header, body = self.textToHtml(testHTML)
        self.htmlToQImage(body)

    def textToHtml(self, text):
        result = self.markup.convert(text)

        return result.get_document_title(), result.get_document_body()

    def htmlToQImage(self, html):
        page = QWebEnginePage()

        page.setContent(html, "text/html")

        img = QImage(500, 500, QImage.Format_ARGB32)
        painter = QPainter(img)
        page.render(painter)
        painter.end()

        return img