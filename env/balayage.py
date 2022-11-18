import cv2
import sys
import numpy as np
import brailleTable
import writechar

# read image 
image = cv2.imread("testTristan.png")
#i -> colonnes; j -> lignes ;
# i = 1
# j = 1
print(image.shape)
h, w, _ = image.shape
for lig in range(h):
    for col in range(w):
        image[lig,col]=[0,0,0]

color=[255,255,255]
image[10,40]=color
image[40,10]=color

# image[203,103]=color
# image[100,29]=color
# image[190,100]=color
# image[0,0]=color
xmin=w-1
ymin=h-1
xmax=0
ymax=0
pasx = 4
pasy = 6

for lig in range(h):
    for col in range(w):
        # print(image[lig,col])
        # print(image[lig,col,0])
        if(image[lig,col,0]==255):
            if(lig > ymax):                
                ymax = lig
            if(col > xmax):               
                xmax = col
            if(lig < ymin):               
                ymin = lig
            if(col < xmin):              
                xmin = col
carac=[xmin,ymin,xmax,ymax]
print(carac)
# cv2.rectangle(image,(xmin-1,ymin-1),(xmax+1,ymax+1),(0,0,255),1)
for l in range(ymin,ymax,pasy):
    if l!=0:
        cv2.line(image,(xmin,l),(xmax,l),(0,0,255),1)

for k in range(xmin,xmax,pasx):
    if k!=0:
        cv2.line(image,(k,ymin),(k,ymax),(0,0,255),1)
color=[255,255,255]
image[10,40]=color
image[40,10]=color
# image[203,103]=color
# image[100,29]=color
# image[190,100]=color
# image[0,0]=color
# image[203,103]=color
# image[100,29]=color
# image[190,100]=color
writechar.write(image,(ymin,xmin),'v')
writechar.write2(image,(ymin,xmin),ymax-ymin,xmax-xmin,'t')
cv2.imshow('////', image)
# add wait key. window waits until user presses a key
cv2.waitKey(0)
# and finally destroy/close all open windows
cv2.destroyAllWindows()


