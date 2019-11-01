class rgb():
    fore = (17,141,166)
    bckg = (2,11,13)
    main = (10,87,125)
    side = (42,41,41)
    page = (5,33,38)

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

    tuple(map(lambda x, y: x / y, fore, normTuple))
    tuple(map(lambda x, y: x / y, bckg, normTuple))
    tuple(map(lambda x, y: x / y, main, normTuple))
    tuple(map(lambda x, y: x / y, side, normTuple))
    tuple(map(lambda x, y: x / y, page, normTuple))

    tuple(map(lambda x, y: x / y, black, normTuple))
    tuple(map(lambda x, y: x / y, white, normTuple))