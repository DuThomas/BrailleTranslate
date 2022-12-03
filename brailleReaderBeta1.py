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
    parentPointCenter = pointGroup[-1]
    for pointIndex in range(len(contours) - 1):
        if pointState[pointIndex]:
            point = contours[pointIndex + 1]
            pointX, pointY, pointW, pointH = cv2.boundingRect(point)
            pointCenter = (pointX + pointW / 2, pointY + pointH / 2)
            
            print("point size : ", pointW, pointH)
            
            if areCloseEnough(parentPointCenter, pointCenter, (pointW, pointH)):
                pointState[pointIndex] = False
                pointGroup.append(pointCenter)
                cv2.line(threshold, coordToInt(parentPointCenter), coordToInt(pointCenter), [0, 0, 255])
                findPoint(pointGroup)
                
def findPointBox(pointGroup):
    print("here : ", pointGroup)
    xmin = pointGroup[0][0] - 1
    ymin = pointGroup[0][1] - 1
    xmax = 0
    ymax = 0

    for point in pointGroup:
            if(point[1] > ymax):                
                ymax = point[1]
            if(point[1] < ymin):               
                ymin = point[1]
            if(point[0] > xmax):               
                xmax = point[0]
            if(point[0] < xmin):              
                xmin = point[0]
    return (xmin, ymin, xmax, ymax)

# testList1 = [2, 2, 3, 9, 3, 2, 3]

# for i in range(len(testList1)):
#     for j in range(i + 1, len(testList1)):
#         if(testList1[j] == testList1[i]):
#             testList1.pop(j)
# print(testList1)

# def findBox(image):
#     h, w= image.shape
#     xmin = w - 1
#     ymin = h - 1
#     xmax = 0
#     ymax = 0

#     for lig in range(h):
#         for col in range(w):
#             if(image[lig, col] == 0):
#                 if(lig > ymax):                
#                     ymax = lig
#                 if(lig < ymin):               
#                     ymin = lig
#                 if(col > xmax):               
#                     xmax = col
#                 if(col < xmin):              
#                     xmin = col
#     return (xmin, ymin, xmax, ymax)

image = cv2.imread('./res/brailleTextePhoto.png')

scale_percent = 50 # percent of original size
width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)
dim = (width, height)

image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

# converting image into grayscale image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# setting threshold of gray image
mythreshold = 140
_, threshold = cv2.threshold(gray, mythreshold, 255, cv2.THRESH_BINARY)

# find the box that contains all the characters

# textBox = findBox(threshold)

xDistances = []
yDistances = []

# using a findContours() function
contours, _ = cv2.findContours(
    threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

pointGroups = []

pointState = list(True for i in range(len(contours) - 1))
print(pointState)

i = 0

while True in pointState:
    mainPointIndex = pointState.index(True) # recupere l'indice d'un point sans groupe
    pointState[mainPointIndex] = False # indique que ce point d'est plus disponible (on va lui trouver son groupe)
    mainPoint = contours[mainPointIndex + 1]
    
    mainPointX, mainPointY, mainPointW, mainPointH = cv2.boundingRect(mainPoint)
    print(mainPointW, mainPointH)
    
    mainPointCenter = (mainPointX + mainPointW / 2, mainPointY + mainPointH / 2)
    
    pointGroup = [mainPointCenter]
    
    findPoint(pointGroup)
    # for pointIndex in range(len(contours) - 1):
    #     if pointState[pointIndex]:
    #         point = contours[pointIndex]
    #         pointX, pointY, pointW, pointH = cv2.boundingRect(point)
    #         pointCenter = (pointX + pointW / 2, pointY + pointH / 2)
            
    #         print("point size : ", pointW, pointH)
            
    #         if areCloseEnough(mainPointCenter, pointCenter, (pointW, pointH)):
    #             pointState[pointIndex] = False
    #             pointGroup.append(pointCenter)
    #             cv2.line(threshold, coordToInt(mainPointCenter), coordToInt(pointCenter), [0, 0, 255])
    pointGroups.append(pointGroup)
                
    
    
    
# for contour in contours:
    
#     (contourX,contourY,contourW,contourH) = cv2.boundingRect(contour)

#     # here we are ignoring first counter because
#     # findcontour function detects whole image as shape
#     if i == 0:
#         i = 1
#         continue
#     i += 1
    
#     if not pointState[i - 2]:
#         continue

#     x = int(contourX + contourW / 2)
#     y = int(contourY + contourH / 2)
    
#     stop = False
#     center = (x, y)
#     for pointGroup in pointGroups:
#         if center in pointGroup:
#             stop = True
#             break
#     if stop:
#         continue
    
#     pointCenter = []
#     j = 0
#     for contour2 in contours:
#         (contour2X, contour2Y, contour2W, contour2H) = cv2.boundingRect(contour2)
#         if j == 0:
#             j = 1
#             continue
#         j += 1
        
#         if not pointState[j - 2]:
#             continue

#         x2 = int(contour2X + contour2W / 2)
#         y2 = int(contour2Y + contour2H / 2)

#         xDistance = (x - x2)
#         yDistance = (y - y2)

#         if(xDistance != 0 and abs(xDistance) not in xDistances):
#             xDistances.append(abs(xDistance))
#             # cv2.line(image, (x, y), (x2 , y2), [255, 0, 0])

#         if(yDistance != 0 and abs(yDistance) not in yDistances):
#             yDistances.append(abs(yDistance))
#             # cv2.line(image, (x, y), (x2 , y2), [0, 0, 255])
#         coef = 1.75
        
#         if(sqrt(xDistance ** 2 + yDistance ** 2) <= sqrt((coef * contourW) ** 2 + (coef * contourH) ** 2)):
#             if((x2, y2) not in pointCenter):
    #             pointCenter.append((x2, y2))
    #         cv2.line(threshold, (x, y), (x2 , y2), [0, 0, 255])

    # # putting shape name at center of each shape
    # text = str(i)
    # cv2.putText(image, text, (x, y),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (25, 155, 155), 2)
    
    # pointCenter.sort()
    # if pointCenter not in pointGroups:
    #     pointGroups.append(pointCenter)

# cv2.rectangle(image,(textBox[0]-1,textBox[1]-1),(textBox[2]+1,textBox[3]+1),(100,100,100),1)
# cv2.rectangle(threshold,(textBox[0]-1,textBox[1]-1),(textBox[2]+1,textBox[3]+1),(100, 100, 100),1)


xDistances.sort()
yDistances.sort()

# rectW = int(2.5 * xDistances[0])
# rectH = int(3.5 * yDistances[0])

# row = textBox[1]

# while row < textBox[3]:
#     col = textBox[0]
#     while col < textBox[2]:
#         brailleChar = threshold[row:row + int(2.5 * yDistances[0]), col:col + int(1.5 * xDistances[0])]
#         cv2.putText(threshold, translator.translate(brailleChar), (col + int(1.5 * xDistances[0] / 2), row + int(2.5 * yDistances[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
#         cv2.rectangle(threshold, (col, row), (col + int(1.5 * xDistances[0]), row + int(2.5 * yDistances[0])), [0, 0, 255])
#         col += rectW
#     row += rectH

pointGroups.sort()

# print(pointGroups)
for i in range(len(pointGroups)):
    print(i, pointGroups[i])
    box = findPointBox(pointGroups[i])
    tlCorner = coordToInt((box[0], box[1]))
    brCorner = coordToInt((box[2], box[3]))
    margin = 15
    tlCorner = (tlCorner[0] - margin, tlCorner[1] - margin)
    brCorner = (brCorner[0] + margin, brCorner[1] + margin)
    cv2.rectangle(threshold, tlCorner, brCorner, [0, 0, 255])

counter = 0
for pointGroup in pointGroups:
    point = (int(pointGroup[0][0]), int(pointGroup[0][1]))
    cv2.putText(threshold, str(counter), point, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
    counter += 1


cv2.imshow('shapes', image)
cv2.imshow('output', threshold)
cv2.imwrite("./res/output.png", threshold)

cv2.waitKey(0)
cv2.destroyAllWindows()
