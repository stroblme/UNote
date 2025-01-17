class rgb():
    fore = (17,141,166)
    bckg = (2,11,13)
    main = (10,87,125)
    side = (42,41,41)
    page = (5,33,38)

    red = (255,0,0)

    black = (0,0,0)
    white = (255,255,255)

class norm_rgb():
    normTuple = (255,255,255)

    fore = rgb.fore
    bckg = rgb.bckg
    main = rgb.main
    side = rgb.side
    page = rgb.page

    black = rgb.black
    white = rgb.white

    red = rgb.red

    fore = tuple(map(lambda x, y: x / y, fore, normTuple))
    bckg = tuple(map(lambda x, y: x / y, bckg, normTuple))
    main = tuple(map(lambda x, y: x / y, main, normTuple))
    side = tuple(map(lambda x, y: x / y, side, normTuple))
    page = tuple(map(lambda x, y: x / y, page, normTuple))

    black = tuple(map(lambda x, y: x / y, black, normTuple))
    white = tuple(map(lambda x, y: x / y, white, normTuple))

class pdf_annots():
    lineWidth = 0.6
    borderWidth = 1
    dashLevel = 1
    defaultPenSize = 1
    defaultMarkerSize = 15
    defaultTextSize = 12
    defaultBoxHeight = 14
    defaultBoxWidth = 130
    freeHandScale = 90
    markerScale = 90
    formScale = 120