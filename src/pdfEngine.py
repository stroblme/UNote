import fitz
from PIL import Image, ImageQt
import PIL.ImageOps


class pdfEngine():
    def __init__(self):
        super().__init__()



    def openPdf(self, filename):
        self.doc = fitz.open(filename)

        return self.doc

    def getPage(self, pageNumber):
        page = self.extractPage(self.doc, pageNumber)

        return page

    def renderPage(self, pageNumber, clip = None, mat = None):
        if not self.doc:
            return None

        page = self.extractPage(self.doc, pageNumber)
        pixmap = self.renderPixmap(page, clip = clip, mat = mat)

        qimage = self.getQImage(pixmap)

        return qimage


    def extractPage(self, doc, pageNumber):
        page = doc.loadPage(pageNumber)

        return page

    def renderPixmap(self, page, mat = None, clip = None, alpha = False):
        pixmap = page.getPixmap(matrix = mat, clip = clip, alpha = alpha)

        return pixmap

    def getQImage(self, pixmap):
        mode = "RGBA" if pixmap.alpha else "RGB"

        img = Image.frombytes(mode, [pixmap.width, pixmap.height], pixmap.samples)
        return ImageQt.ImageQt(img)