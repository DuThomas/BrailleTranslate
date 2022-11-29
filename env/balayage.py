import cv2
import sys
import numpy as np
import brailleTable
import writechar

# read image 
# image = cv2.imread("testTristan.png")
image = np.zeros((200, 200 , 3), np.uint8)
#i -> colonnes; j -> lignes ;
# i = 1
# j = 1
print(image.shape)
h, w, _ = image.shape
for lig in range(h):
    for col in range(w):
        image[lig, col] = [0, 0, 0]

color = [255, 255, 255]
image[10,40] = color
image[40,10] = color

xmin = w - 1
ymin = h - 1
xmax = 0
ymax = 0
pasx = 4
pasy = 6

for lig in range(h):
    for col in range(w):
        if(image[lig,col,0] == 255):
            if(lig > ymax):                
                ymax = lig
            if(lig < ymin):               
                ymin = lig
            if(col > xmax):               
                xmax = col
            if(col < xmin):              
                xmin = col
carac = [xmin, ymin, xmax, ymax]
print(carac)
# cv2.rectangle(image,(xmin-1,ymin-1),(xmax+1,ymax+1),(0,0,255),1)
for l in range(ymin, ymax, pasy):
    if l != 0:
        cv2.line(image, (xmin, l), (xmax, l), (0, 0, 255), 1)

for k in range(xmin, xmax, pasx):
    if k != 0:
        cv2.line(image, (k, ymin), (k, ymax), (0, 0, 255), 1)
color = [255, 255, 255]
image[10, 40] = color
image[40, 10] = color
# image[203,103]=color
# image[100,29]=color
# image[190,100]=color
# image[0,0]=color
# image[203,103]=color
# image[100,29]=color
# image[190,100]=color
writechar.write2(image, (ymin, xmin), 12, 12)

scale_percent = 1200 # percent of original size
width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)
dim = (width, height)

# resize image
resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

cv2.imshow('////', resized)
# add wait key. window waits until user presses a key
cv2.waitKey(0)
# and finally destroy/close all open windows
cv2.destroyAllWindows()


