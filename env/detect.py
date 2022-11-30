import cv2
import sys
import numpy as np
import brailleTable
import writechar

def drawLimitDot(image, color):

    writechar.drawDot(image, (200, 200), color)
    writechar.drawDot(image, (10, 10), color)
    writechar.drawDot(image, (10, 200), color)
    writechar.drawDot(image, (200, 10), color)

# read image 
image = cv2.imread("./allChar.png")

white = [255, 255, 255]
black = [0, 0, 0]

print(image.shape)
h, w, _ = image.shape

xmin = w - 1
ymin = h - 1
xmax = 0
ymax = 0
pasx = 5
pasy = 7

for lig in range(h):
    for col in range(w):
        if(image[lig,col,0] == 0):
            if(lig > ymax):                
                ymax = lig
            if(lig < ymin):               
                ymin = lig
            if(col > xmax):               
                xmax = col
            if(col < xmin):              
                xmin = col
            col += writechar.DOT_SIZE

carac = [xmin, ymin, xmax, ymax]
print(carac)
cv2.rectangle(image,(xmin-1,ymin-1),(xmax+1,ymax+1),(0,0,255),1)
# for l in range(ymin, ymax - writechar.DOT_SIZE, pasy * writechar.DOT_SIZE):
#     if l != 0:
#         cv2.line(image, (xmin, l), (xmax, l), (0, 0, 255), 1)
#         cv2.rectangle(image, (xmin, l), (xmax, l + writechar.DOT_SIZE - 1), (0, 0, 255), 1)

# for k in range(xmin, xmax - writechar.DOT_SIZE, pasx * writechar.DOT_SIZE):
#     if k != 0:
#         cv2.line(image, (k, ymin), (k, ymax), (0, 0, 255), 1)
#         cv2.rectangle(image, (k, ymin), (k + writechar.DOT_SIZE - 1, ymax), (0, 0, 255), 1)

# writechar.drawDot(image, (ymin, xmin), [255, 0, 0])

scale_percent = 100 # percent of original size
width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)
dim = (width, height)

# resize image
resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

cv2.imshow('////', resized)
# add wait key. window waits until user presses a key
cv2.waitKey(0)
# and finally destroy/close all open windows

# firstChar = image[ymin + writechar.DOT_SIZE:ymin + 6 * writechar.DOT_SIZE, xmin + writechar.DOT_SIZE:xmin + 4 * writechar.DOT_SIZE]
# cv2.imshow('////', firstChar)
# add wait key. window waits until user presses a key
# cv2.waitKey(0)
cv2.destroyAllWindows()
