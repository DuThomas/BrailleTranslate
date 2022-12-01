import cv2
import numpy as np
import brailleTable

DOT_SIZE = 12

def writeBrailleText(image, tlcorner, color):
    col = 0
    row = 0
    while(True):
        cv2.imshow('brailleWriter', image)
        key = cv2.waitKey(0)
        print(key)
        if(ord('a') <= key <= ord('z') or key == 32):
            writeBrailleChar(image, (tlcorner[0] + row * DOT_SIZE, tlcorner[1] + col * DOT_SIZE), chr(key), color)
            col += 5
        elif(key == 13):
            col = 0
            row += 7
        elif(key == 27):
            break
        

def writeBrailleChar(img, tlcorner, char, color):
    m = ""
    for cle,val in brailleTable.brailleTable.items():
        if (val == char):
            m = cle
    x = 0
    y = 0
    for i in range(len(m)):
        if(m[i] == '1'):
            drawDot(img, (tlcorner[0] + (i%3 * 2 + 1) * DOT_SIZE, tlcorner[1] + (i//3 * 2 + 1) * DOT_SIZE), color)

def drawSqareDot(img, tlCorner, color):
    img[tlCorner[0]:tlCorner[0] + DOT_SIZE , tlCorner[1]:tlCorner[1] + DOT_SIZE] = color

def drawDot(img, tlCorner, color):
    cv2.circle(img, (int(tlCorner[1] + DOT_SIZE/2), int(tlCorner[0] + DOT_SIZE/2)), int(DOT_SIZE/2), color, -1)

def newImage(width, height, bgColor):
    image = np.zeros((width, height , 3), np.uint8)
    for row in range(height):
        for col in range(width):
            image[col, row] = bgColor
    return image
            
white = [255, 255, 255]
black = [0, 0, 0]

width = 400
height = 500
image = newImage(width, height, white)

x = 50
y = 20

writeBrailleText(image, (y, x), black)

cv2.destroyAllWindows()
cv2.imwrite("./res/brailleText.png", image)
