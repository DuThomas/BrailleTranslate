import cv2
import brailleTable

DOT_SIZE = 12

def write(img, tlcorner, char):
    print(tlcorner)
    color=[255, 255, 255]
    m = ""
    for cle,val in brailleTable.brailleTable.items():
        if (val == char):
            m = cle
    x = 0
    y = 0
    for i in range(len(m)):
        if(m[i] == '1'):
            img[tlcorner[0]+ i%3 * 2 + 1, tlcorner[1] + i//3 * 2 + 1] = color

def write2(img, tlcorner, h, w):
    for lignes in range(0, h, 7):
        for colonnes in range(0, w, 5):
            scale_percent = 100 # percent of original size
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)
            # resize image
            resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            cv2.imshow('////', resized)
            # add wait key. window waits until user presses a key
            key = cv2.waitKey(0)
            # print(ord('a'), ord('z'))
            writeChar(img, (tlcorner[0] + lignes * DOT_SIZE, tlcorner[1] + colonnes * DOT_SIZE), chr(key))

def writeChar(img, tlcorner, char):
    print(tlcorner)
    color = [0, 0, 0]
    m = ""
    for cle,val in brailleTable.brailleTable.items():
        if (val == char):
            m = cle
    x = 0
    y = 0
    for i in range(len(m)):
        if(m[i] == '1'):
            drawDot2(img, (tlcorner[0] + (i%3 * 2 + 1) * DOT_SIZE, tlcorner[1] + (i//3 * 2 + 1) * DOT_SIZE), color)

def drawDot(img, tlCorner, color):
    img[tlCorner[0]:tlCorner[0] + DOT_SIZE , tlCorner[1]:tlCorner[1] + DOT_SIZE] = color

def drawDot2(img, tlCorner, color):
    cv2.circle(img, (int(tlCorner[1] + DOT_SIZE/2), int(tlCorner[0] + DOT_SIZE/2)), int(DOT_SIZE/2), color, -1)
