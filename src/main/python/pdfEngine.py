import os
import fitz
from PIL import Image, ImageQt


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
                print("Replacing temp file")
                name, ext = os.path.splitext(self.filename)
                name = name + '_m'

                os.replace(name + ext, self.filename)

    def newPdf(self, filename):
        self.doc = fitz.open()
        self.filename = filename

        # Insert empty page
        self.doc.newPage(0)

        self.savePdfAs(self.filename)

    def rotatePage(self, page):
        page.setRotation(180)
        return page

    def resizePage(self, page, width, height):
        r = page.rect
        r = fitz.Rect(r.x0, r.y0-height, r.x1+width, r.y1+height)
        page.setMediaBox(r)
        return page

    def openPdf(self, filename):
        # import fitz
        self.filename = filename
        self.doc = fitz.open(filename)

        return self.doc

    def closePdf(self):
        self.doc.close()


    def savePdf(self,cleanup=False):
        name, ext = os.path.splitext(self.filename)
        try:
            if self.incremental:
                self.doc.save(name + ext, incremental = self.incremental)
                return self.filename
            else:
                name = name + '_m'
                if cleanup:
                    self.doc.save(name + ext, incremental = self.incremental,garbage=1, deflate=1, clean=1)
                else:
                    self.doc.save(name + ext, incremental = self.incremental)

                #Suggest new filename
                return (name + ext)
        except RuntimeError as identifier:
            print(str(identifier))
            if self.incremental:
                self.incremental = False
    
                return self.savePdf(cleanup)

        except ValueError as identifier:
            print(str(identifier))
            self.incremental = False


        print('PDF saved')

    def savePdfAs(self, filename):
        name, ext = os.path.splitext(filename)

        ext = '.pdf'

        self.filename = name + ext

        self.doc.save(self.filename)

        print('PDF saved as ' + self.filename)


    def getPage(self, pageNumber):
        '''
        For external call
        '''
        try:
            page = self.doc[pageNumber]
            return page
        except IndexError:
            print('Unable to get page number ' + str(pageNumber))

        return None

    def renderPage(self, pageNumber, clip = None, mat = None):
        if not self.doc or not pageNumber:
            return None

        return self.getQImage(self.renderPixmap(pageNumber, clip = clip, mat = mat))

    def insertPage(self, pageNumber):
        width = height = None

        try:
            page = self.doc[0]

            width, height = self.getPageSize(0)
        except IndexError:
            width = height = None


        page = self.doc.newPage(pageNumber, width=width, height=height)

        return page

    def deletePage(self, pageNumber):
        try:
            self.doc.deletePage(pageNumber)
            return True
        except IndexError:
            return False

    def getPageSize(self, pageNumber = None):
        if pageNumber:
            page = self.doc[pageNumber]
        else:
            page = self.doc[0]

        return page.bound().width, page.bound().height

    def renderPixmap(self, pageNumber=0, mat = None, clip = None, alpha = False):
        try:
            return self.doc[pageNumber].getPixmap(matrix = mat, clip = clip, alpha = alpha)
        except RuntimeError as identifier:
            raise RuntimeError(identifier)


    def getQImage(self, pixmap):
        mode = "RGBA" if pixmap.alpha else "RGB"

        img = Image.frombytes(mode, [pixmap.width, pixmap.height], pixmap.samples)
        return ImageQt.ImageQt(img)