import cv2
import brailleTable
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
    for lignes in range(0, h, 6):
        for colonnes in range(0, w, 4):
            scale_percent = 1200 # percent of original size
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)
            # resize image
            resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            cv2.imshow('////', resized)
            # add wait key. window waits until user presses a key
            key = cv2.waitKey(0)
            # print(ord('a'), ord('z'))
            write3(img, (tlcorner[0] + lignes, tlcorner[1] + colonnes), chr(key))

def write3(img, tlcorner, char):
    print(tlcorner)
    color = [255, 255, 255]
    m = ""
    # char = input()
    for cle,val in brailleTable.brailleTable.items():
        if (val == char):
            m = cle
    x = 0
    y = 0
    for i in range(len(m)):
        if(m[i] == '1'):
            img[tlcorner[0] + i%3 * 2 + 1, tlcorner[1] + i//3 * 2 + 1] = color
