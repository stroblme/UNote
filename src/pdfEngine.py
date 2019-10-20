import fitz
from PIL import Image, ImageQt
import PIL.ImageOps


class pdfEngine():
    dark = True

    def __init__(self):
        super().__init__()

    def renderPdf(self, filename, pageNumber):
        doc = fitz.open(filename)
        page = doc.loadPage(pageNumber)
        pixmap = page.getPixmap()
        mode = "RGBA" if pixmap.alpha else "RGB"
        img = Image.frombytes(mode, [pixmap.width, pixmap.height], pixmap.samples)
        return ImageQt.ImageQt(img)
