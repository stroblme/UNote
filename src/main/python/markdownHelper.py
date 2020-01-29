# from PySide2.QtWebEngineWidgets import QWebEnginePage
from PySide2.QtCore import Qt, Signal, QObject
# from PySide2.QtWebChannel import QWebChannel
# from PySide2.QtWebEngine import QWebFrame
from PySide2.QtWidgets import QWidget


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

        # self.ppage = PreviewPage(self)

    def loadGetMarkdownPage(self, markdown):
        content = Document()
        content.setText(markdown)

        # channel = QWebChannel(self)
        # channel.registerObject('content', content)

        # self.ppage.setWebChannel(channel)

        # return self.ppage

class Document(QObject):
    textChanged = Signal(str)

    m_text = ""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def setText(self, qstr):
        if (qstr == self.m_text):
            return
        self.m_text = qstr;
        self.textChanged.emit(self.m_text);


# class PreviewPage(QWebEnginePage):

#     def acceptNavigationRequest(qurl, navigationType, isMainFrame):

#         pass

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