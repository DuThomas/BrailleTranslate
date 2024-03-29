from . import brailleTable


def translate2(image):

    i = 1
    j = 1

    h, w = image.shape
    character = []

    for col in range(2):
        i = int(col * w/2)
        for row in range(3):
            j = int(row * h/3)
            while (i < (col + 1) * w/2 and j < (row + 1) * h/3 and image[j, i] != 0):
                i += 1
                if(i == int((col + 1) * w/2)):
                    i = int(col * w/2)
                    j += 1
            if(i < (col + 1) * w/2 and j < (row + 1) * h/3):
                character.append(1)
            else:
                character.append(0)

    output = ""
    for i in character:
        output += str(i)

    value = brailleTable.brailleTable.get(output)
        
    if value:
        return(value)
    else:
        return("?")

def translate(image):
    i = 1
    j = 1

    h, w = image.shape
    character = []
    minRate = 0.10 # 10 % d'une case doit etre noir pour etre consideree comme un point
    for col in range(2):
        i = int(col * w/2)
        for row in range(3):
            j = int(row * h/3)
            blackCounter = 0
            while (i < (col + 1) * w/2 and j < (row + 1) * h/3):
                if image[j, i] == 0:
                    blackCounter += 1
                i += 1
                if(i == int((col + 1) * w/2)):
                    i = int(col * w/2)
                    j += 1
            # print(blackCounter / ((w/2) * (h/3)))
            if (h * w / 6) > 0 and blackCounter / (h * w / 6) > minRate:
                character.append(1)
            else:
                character.append(0)
        
    # cv2.imshow("img", image)
    # cv2.waitKey(0)

    output = ""
    for i in character:
        output += str(i)

    value = brailleTable.brailleTable.get(output)
        
    if value:
        return(value)
    else:
        return("?")
