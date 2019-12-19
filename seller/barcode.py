from reportlab.lib.units import mm
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing

class GBLBARCODE(Drawing):
    def __init__(self, text_value, *args, **kw):
        barcode = createBarcodeDrawing('Code128', value=text_value, barHeight=10 * mm, humanReadable=True)
        Drawing.__init__(self, barcode.width, barcode.height, *args, **kw)
        self.add(barcode, name='GOBDLOGISTICS')


if __name__ == '__main__':
    GBLBARCODE("GO BD LOGISTICS").save(formats=['gif'], outDir='.', fnRoot='barcode')