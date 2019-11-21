import fitz
from PIL import Image, ImageQt
import PIL.ImageOps
import os


class pdfEngine():
    filename = None
    doc = None
    incremental = True

    def __init__(self):
        super().__init__()

    def __del__(self):
        if self.doc:
            self.doc.close()

            if not self.incremental:
                name, ext = os.path.splitext(self.filename)
                name = name + '_m'

                os.replace(name + ext, self.filename)

    def newPdf(self, filename):
        self.doc = fitz.open()
        self.filename = filename

        # Insert empty page
        self.doc.newPage(-1)

        self.savePdfAs(self.filename)

    def openPdf(self, filename):
        # import fitz
        self.filename = filename
        self.doc = fitz.open(filename)

        return self.doc

    def savePdf(self):
        name, ext = os.path.splitext(self.filename)
        try:
            if self.incremental:
                self.doc.save(self.filename, incremental = self.incremental)
                return self.filename
            else:
                name = name + '_m'
                self.doc.save(name + ext, incremental = self.incremental)

                #Suggest new filename
                return (name + ext)
        except:
            print('Can\'t do incremental. Will save with _m appended')
            self.incremental = False
            return self.savePdf()

    def savePdfAs(self, filename):
        name, ext = os.path.splitext(filename)

        ext = '.pdf'

        self.filename = name + ext

        self.doc.save(self.filename)

        print('PDF saved as ' + self.filename)


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

    def insertPage(self, pageNumber):
        width = height = None

        page = self.extractPage(self.doc, pageNumber)

        width, height = self.getPageSize(self.doc, pageNumber)

        page = self.doc.newPage(pageNumber, width=width, height=height)

        return page

    def extractPage(self, doc, pageNumber):
        page = doc.loadPage(pageNumber)

        return page

    def getPageSize(self, doc, pageNumber = None):
        if pageNumber:
            page = self.extractPage(doc, pageNumber)
        else:
            page = self.extractPage(doc, 0)

        return page.bound().width, page.bound().height

    def renderPixmap(self, page, mat = None, clip = None, alpha = False):
        pixmap = page.getPixmap(matrix = mat, clip = clip, alpha = alpha)
        return pixmap


    def getQImage(self, pixmap):
        mode = "RGBA" if pixmap.alpha else "RGB"

        img = Image.frombytes(mode, [pixmap.width, pixmap.height], pixmap.samples)
        return ImageQt.ImageQt(img)

    # def insertText(self, page, text, textRect):
    #     red  = (1,0,0)                                   # some colors
    #     gold = (1,1,0)
    #     blue = (0,0,1)
    #     """We use a Shape object (something like a canvas) tot output the text and
    #     the rectangles surounding it for demonstration.
    #     """

    #     shape = page.newShape()                            # create Shape
    #     shape.drawRect(textRect)                                 # draw rectangles
    #     shape.finish(width = 1, color = red, fill = gold)
    #     # Now insert text in the rectangles. Font "Helvetica" will be used
    #     # by default. A return code rc < 0 indicates insufficient space (not checked here).
    #     rc = shape.insertTextbox(textRect, fontsize=100, buffer=text, color = blue, rotate=180)
    #     shape.commit()                                     # write all stuff to page /Contents
    #     # print(shape.width)
    #     # print(shape.height)
    #     # print(page.bound().height)
    #     # print(page.bound().width)
    #     # print(self.doc.metadata['encryption'])
    #     # self.doc.metadata['encryption'] = False

    #     # page.insertText(fitz.Point(490,490),                   # bottom-left of 1st char
    #     #              'hihiu',                # the text (honors '\n')
    #     #              fontname = "helv",   # the default font
    #     #              fontsize = 100,       # the default font size
    #     #              rotate = 0,          # also available: 90, 180, 270
    #     #              )

    #     name, ext = os.path.splitext(self.filename)
    #     name = name + '_c'

        # self.doc.save(name)