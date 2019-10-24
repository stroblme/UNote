import fitz
from PIL import Image, ImageQt
import PIL.ImageOps
import os


class pdfEngine():
    def __init__(self):
        super().__init__()

    height = 900
    width = 637

    def openPdf(self, filename):
        self.filename = filename
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

    def insertText(self, page, text, textRect):
        red  = (1,0,0)                                   # some colors
        gold = (1,1,0)
        blue = (0,0,1)
        """We use a Shape object (something like a canvas) to output the text and
        the rectangles surounding it for demonstration.
        """
        shape = page.newShape()                            # create Shape
        shape.drawRect(textRect)                                 # draw rectangles
        shape.finish(width = 0.3, color = red, fill = gold)
        # Now insert text in the rectangles. Font "Helvetica" will be used
        # by default. A return code rc < 0 indicates insufficient space (not checked here).
        rc = shape.insertTextbox(textRect, text, color = blue)
        shape.commit()                                     # write all stuff to page /Contents

        # print(self.doc.metadata['encryption'])
        # self.doc.metadata['encryption'] = False

        name, ext = os.path.splitext(self.filename)
        name = name + '_c'

        self.doc.save(name + ext)