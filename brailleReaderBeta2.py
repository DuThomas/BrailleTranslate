import cv2
import translator
from math import *

def areCloseEnough(point1, point2, point1Size):
    coef = 1.75
    xDistance = point1[0] - point2[0]
    yDistance = point1[1] - point2[1]
    print(sqrt(xDistance ** 2 + yDistance ** 2), sqrt((coef * point1Size[0]) ** 2 + (coef * point1Size[1]) ** 2))
    print(point1Size)
    return sqrt(xDistance ** 2 + yDistance ** 2) <= sqrt((coef * point1Size[0]) ** 2 + (coef * point1Size[1]) ** 2)

def coordToInt(coord):
    return(int(coord[0]), int(coord[1]))

def findPoint(pointGroup):
    parentPoint = pointGroup[-1]
    parentPointX, parentPointY, parentPointW, parentPointH = cv2.boundingRect(parentPoint)
    parentPointCenter = (parentPointX + parentPointW / 2, parentPointY + parentPointH / 2)
    for pointIndex in range(len(contours) - 1):
        if pointState[pointIndex]:
            point = contours[pointIndex + 1]
            pointX, pointY, pointW, pointH = cv2.boundingRect(point)
            pointCenter = (pointX + pointW / 2, pointY + pointH / 2)
            
            print("point size : ", pointW, pointH)
            
            if areCloseEnough(parentPointCenter, pointCenter, (pointW, pointH)):
                pointState[pointIndex] = False
                pointGroup.append(point)
                # cv2.line(threshold, coordToInt(parentPointCenter), coordToInt(pointCenter), [0, 0, 255])
                findPoint(pointGroup)
                
def findPointBox(pointGroup):
    pointX, pointY, pointW, pointH = cv2.boundingRect(pointGroup[0])
    pointCenter = (pointX + pointW / 2, pointY + pointH / 2)
    xmin = pointCenter[0] - 1
    ymin = pointCenter[1] - 1
    xmax = 0
    ymax = 0

    for point in pointGroup:
        pointX, pointY, pointW, pointH = cv2.boundingRect(point)
        pointCenter = (pointX + pointW / 2, pointY + pointH / 2)
        if(pointCenter[1] > ymax):                
            ymax = pointCenter[1]
        if(pointCenter[1] < ymin):               
            ymin = pointCenter[1]
        if(pointCenter[0] > xmax):               
            xmax = pointCenter[0]
        if(pointCenter[0] < xmin):              
            xmin = pointCenter[0]
    xp = 1.75
    yp = 3.5
    if xmax - xmin < xp * pointW:
        xmax = xmin + xp * pointW
    if ymax - ymin < yp * pointH:
        ymax = ymin + yp * pointH
    
    return (xmin, ymin, xmax, ymax)

def intersect(box1, box2):
    # print(box1)
    # print(box2)
    # cv2.rectangle(threshold, coordToInt((box1[0], box1[1])), coordToInt((box1[2], box1[3])), [0, 0, 255])
    # cv2.rectangle(threshold, coordToInt((box2[0], box2[1])), coordToInt((box2[2], box2[3])), [0, 0, 255])
    box1W = (box1[2] - box1[0])
    box1H = (box1[3] - box1[1])
    box1Center = (box1[0] + box1W / 2, box1[1] + box1H / 2)
    
    box2W = (box2[2] - box2[0])
    box2H = (box2[3] - box2[1])
    box2Center = (box2[0] + box2W / 2, box2[1] + box2H / 2)
    
    xDistance = abs(box1Center[0] - box2Center[0])
    yDistance = abs(box1Center[1] - box2Center[1])
    
    return (xDistance < box1W / 2 + box2W / 2 and yDistance < box1H / 2 + box2H / 2)
    
image = cv2.imread('./res/brailleTextePhoto.png')

scale_percent = 45 # percent of original size
width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)
dim = (width, height)

image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

# converting image into grayscale image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# setting threshold of gray image
mythreshold = 140
_, threshold = cv2.threshold(gray, mythreshold, 255, cv2.THRESH_BINARY)

# using a findContours() function
contours, _ = cv2.findContours(
    threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

pointGroups = []

pointState = list(True for i in range(len(contours) - 1))

i = 0

while True in pointState:
    mainPointIndex = pointState.index(True) # recupere l'indice d'un point sans groupe
    pointState[mainPointIndex] = False # indique que ce point d'est plus disponible (on va lui trouver son groupe)
    mainPoint = contours[mainPointIndex + 1]

    pointGroup = [mainPoint]
    findPoint(pointGroup)
    pointGroups.append(pointGroup)

# print(pointGroups)

groupBoxes = []
for i in range(len(pointGroups)):
    groupBoxes.append(findPointBox(pointGroups[i]))

for i in range(len(groupBoxes)):
    for j in range(len(groupBoxes) - 1):
        if(groupBoxes[j][1] > groupBoxes[j + 1][1]):
            tempBox = groupBoxes[j]
            groupBoxes[j] = groupBoxes[j + 1]
            groupBoxes[j + 1] = tempBox

newGroupeBoxes = groupBoxes.copy()
for i in range(len(groupBoxes)):
    for j in range(len(groupBoxes)):
        if(i == j):
            continue
        if intersect(groupBoxes[i], groupBoxes[j]):
            print(i, "intersects ", j)

            if groupBoxes[j] in newGroupeBoxes:
                newGroupeBoxes.remove(groupBoxes[j])
            groupBoxes[j] = (0, 0, 0, 0)

for i in range(len(newGroupeBoxes)):
    tlCorner = coordToInt((newGroupeBoxes[i][0], newGroupeBoxes[i][1]))
    brCorner = coordToInt((newGroupeBoxes[i][2], newGroupeBoxes[i][3]))
    margin = 15
    tlCorner = (tlCorner[0] - margin, tlCorner[1] - margin)
    brCorner = (brCorner[0] + margin, brCorner[1] + margin)
    brailleChar = threshold[tlCorner[1]:brCorner[1], tlCorner[0]:brCorner[0]]
    cv2.putText(threshold, translator.translate(brailleChar), brCorner, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
    
    cv2.rectangle(threshold, tlCorner, brCorner, [0, 0, 255])
    cv2.putText(threshold, str(i), tlCorner, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
    

counter = 0
# for pointGroup in pointGroups:
#     point = (int(pointGroup[0][0]), int(pointGroup[0][1]))
#     cv2.putText(threshold, str(counter), point, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
#     counter += 1


cv2.imshow('shapes', image)
cv2.imshow('output', threshold)
cv2.imwrite("./res/output.png", threshold)

cv2.waitKey(0)
cv2.destroyAllWindows()
