from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QRectF, QEvent, QThread, pyqtSignal, pyqtSlot,QObject, QPoint, pyqtProperty
from PyQt5.QtGui import QPixmap, QImage, QPainter, QDesktopServices
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
# from PyQt5.QtWebEngine import QWebFrame
from PyQt5.QtWidgets import QWidget


import markups

testHTML = '''# Title

## Subtitle

some text

- a
- listing

---

and more text'''

class markdownHelper(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.ppage = PreviewPage(self)

    def loadGetMarkdownPage(self, markdown):
        content = Document()
        content.setText(markdown)

        channel = QWebChannel(self)
        channel.registerObject('content', content)

        self.ppage.setWebChannel(channel)

        return self.ppage

class Document(QObject):
    textChanged = pyqtSignal(str)

    m_text = ""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def setText(self, qstr):
        if (qstr == self.m_text):
            return
        self.m_text = qstr;
        self.textChanged.emit(self.m_text);


class PreviewPage(QWebEnginePage):

    def acceptNavigationRequest(qurl, navigationType, isMainFrame):

        if (qurl.scheme() == "qrc"):
            return True

        openUrl(qurl)
        return False

# {
#     Q_OBJECT
#     Q_PROPERTY(QString text MEMBER m_text NOTIFY textChanged FINAL)
# public:
#     explicit Document(QObject *parent = nullptr) : QObject(parent) {}

#     void setText(const QString &text);

# signals:
#     void textChanged(const QString &text);

# private:
#     QString m_text;
# };