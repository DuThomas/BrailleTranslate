import cv2
import translator
from math import *

def areCloseEnough(point1, point2, point1Size):
    xCoef = 2
    yCoef = 2
    xDistance = abs(point1[0] - point2[0])
    yDistance = (point1[1] - point2[1])
    return (xDistance <= point1Size[0] * xCoef and yDistance <= point1Size[1] * yCoef)

def coordToInt(coord):
    return(int(coord[0]), int(coord[1]))

def findPoint(pointGroup, contours, pointState, image, roiTLC):
    parentPoint = pointGroup[-1]
    parentPointX, parentPointY, parentPointW, parentPointH = cv2.boundingRect(parentPoint)
    parentPointCenter = (parentPointX + parentPointW / 2, parentPointY + parentPointH / 2)
    for pointIndex in range(len(contours) - 1):
        if pointState[pointIndex]:
            point = contours[pointIndex + 1]
            pointX, pointY, pointW, pointH = cv2.boundingRect(point)
            pointCenter = (pointX + pointW / 2, pointY + pointH / 2)
            if areCloseEnough(parentPointCenter, pointCenter, (pointW, pointH)):
                pointState[pointIndex] = False
                pointGroup.append(point)
                findPoint(pointGroup, contours, pointState, image, roiTLC)
                cv2.line(image, ((int)(parentPointCenter[0]), (int)(parentPointCenter[1])), ((int)(pointCenter[0]), (int)(pointCenter[1])), (0, 0, 0), 1)
                
def findPointBox(pointGroup, widths, heights, image, roiTLC):
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
    yp = 3.2
    margin = 7
    cv2.rectangle(image, ((int)(xmin - margin), (int)(ymin - margin)), ((int)(xmax + margin), (int)(ymax + margin)), (0, 0, 0), 1)
    if xmax - xmin < xp * pointW:
        xmax = xmin + xp * pointW
    if ymax - ymin < yp * pointH:
        ymax = ymin + yp * pointH
        
    boxW = xmax - xmin
    boxH = ymax - ymin
    
    widths.append(boxW)
    heights.append(boxH)
    
    
    return (xmin, ymin)

def intersect(box1, box2, width, height):
    box1Center = (box1[0] + width / 2, box1[1] + height / 2)
    box2Center = (box2[0] + width / 2, box2[1] + height / 2)
    
    margin = int(width / 4)
    
    xDistance = abs(box1Center[0] - box2Center[0])
    yDistance = abs(box1Center[1] - box2Center[1])
    
    return (xDistance < width + 2 * margin and yDistance < height + 2 * margin)

def zoom(image, zoom):
    width = int(image.shape[1] * zoom / 100)
    height = int(image.shape[0] * zoom / 100)
    dim = (width, height)
    image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    return image

def translate(image, roi, roiTLC, contours, mythreshold):
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # setting threshold of gray image
    _, threshold = cv2.threshold(gray, mythreshold, 255, cv2.THRESH_BINARY)
    
    cv2.imshow("Thresholded ROI", threshold)
    # using a findContours() function

    pointState = list(True for i in range(len(contours) - 1))
    pointGroups = []
    while True in pointState:
        mainPointIndex = pointState.index(True) # recupere l'indice d'un point sans groupe
        pointState[mainPointIndex] = False # indique que ce point d'est plus disponible (on va lui trouver son groupe)
        mainPoint = contours[mainPointIndex + 1]

        pointGroup = [mainPoint]
        findPoint(pointGroup, contours, pointState, image, roiTLC)
        pointGroups.append(pointGroup)
        
    groupBoxes = []
    boxWidths = []
    boxHeights = []
    for i in range(len(pointGroups)):
        groupBoxes.append(findPointBox(pointGroups[i], boxWidths, boxHeights, image, roiTLC))

    for i in range(len(groupBoxes)): # trie a bulle en fonction de la position y des rectangles
        for j in range(len(groupBoxes) - 1):
            if(groupBoxes[j][1] > groupBoxes[j + 1][1]):
                tempBox = groupBoxes[j]
                groupBoxes[j] = groupBoxes[j + 1]
                groupBoxes[j + 1] = tempBox

    if(len(boxWidths) != 0 and len(boxHeights) != 0):
        width = int(max(boxWidths))
        height = int(max(boxHeights))

    newGroupeBoxes = groupBoxes.copy()
    for i in range(len(groupBoxes)):
        for j in range(len(groupBoxes)):
            if(i == j):
                continue
            if intersect(groupBoxes[i], groupBoxes[j], width, height):
                if groupBoxes[j] in newGroupeBoxes:
                    newGroupeBoxes.remove(groupBoxes[j])
                groupBoxes[j] = (-width, -height)

    for i in range(len(newGroupeBoxes)):
        tlCorner = coordToInt((newGroupeBoxes[i][0], newGroupeBoxes[i][1]))
        margin = int(width / 4)
        tlCorner = (tlCorner[0] - margin - roiTLC[0], tlCorner[1] - margin - roiTLC[1])
        brCorner = (tlCorner[0] + width + margin - roiTLC[0], tlCorner[1] + height + margin - roiTLC[1])

        tlCorner2 = (tlCorner[0] + roiTLC[0], tlCorner[1] + roiTLC[1])
        brCorner2 = (tlCorner[0] + width + 2 * margin + roiTLC[0], tlCorner[1] + height + 2 * margin + roiTLC[1])
        
        brailleChar = threshold[tlCorner[1]:tlCorner[1] + height + 2 * margin, tlCorner[0]:tlCorner[0] + width + 2 * margin]
        cv2.putText(image, translator.translate(brailleChar), brCorner2, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
        cv2.rectangle(image, tlCorner2, brCorner2, [0, 0, 255])

    return image