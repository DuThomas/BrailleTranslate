import cv2
from math import *
import translator
import brailleReaderV3debug as brailleReaderV3

def Point :
    def __init__(self, contour):
        (self.x, self.y, self.width, self.height) = cv2.boundingRect(contour)
        self.haveAGroup = False
        

def isSquare(width, height):
    gap = 20 # in %
    #print(str(height * 100 / 120) + " - - " + str(width) + " - - " + str(height * 100 / 80))
    return width * height > sizeThreshold and height * 100 / (100 + gap) < width < height * 100 / (100 - gap)

def isBigEnough(width, height):
    minLenght = 7
    return width > minLenght and height > minLenght

def drawPointsBox(image, box):
    if isinstance(box, tuple):
        cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 0, 0), 3)

def getPointsBox(points):
    if len(points) > 0:
        xMin = points[0][0]
        xMax = points[0][0]
        yMin = points[0][1]
        yMax = points[0][1]
        for point in points:
            #cv2.rectangle(image, ((int)(point[0] - point[2] / 2), (int)(point[1] - point[3] / 2)),
            #((int)(point[0] + point[2] / 2), (int)(point[1] + point[3] / 2)), (0, 0, 0), 1)
            if point[0] > xMax:
                xMax = point[0]
            if point[0] < xMin:
                xMin = point[0]
            if point[1] > yMax:
                yMax = point[1]
            if point[1] < yMin:
                yMin = point[1]
        return (xMin, yMin, xMax, yMax)
    else:
        print("dddd")

def addMargin(box, margin, image):
    w, h, _ = image.shape
    xMin, yMin, xMax, yMax = box[0], box[1], box[2], box[3]
    if(box[0] - margin < 0):
        xMin = 0
    else:
        xMin = box[0] - margin

    if(box[1] - margin < 0):
        yMin = 0
    else:
        yMin = box[1] - margin

    if(box[2] + margin > h):
        xMax = w - 1
    else:
        xMax = box[2] + margin

    if(box[3] + margin > w):
        yMax = h - 1
    else:
        yMax = box[3] + margin
    return (xMin, yMin, xMax, yMax)

def calcArea(point):
    return point[2] * point[3]

def calcAvgArea(points):
    if len(points) > 0:
        area = 0 
        for point in points:
            area += calcArea(point)
        return area / len(points)

# converting image into grayscale image

cap = cv2.VideoCapture(0)
image0 = cv2.imread('./res/videoImage.png')

# converting image into grayscale image
gray0 = cv2.cvtColor(image0, cv2.COLOR_BGR2GRAY)

sizeThreshold = 120
mythreshold = 80

while True:
    points = []
    ret, image = cap.read()
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #gray = gray0.copy()
    #image = image0.copy()
    
    _, thresholdedImage = cv2.threshold(gray, mythreshold, 255, cv2.THRESH_BINARY)

    # using a findContours() function
    contours, _ = cv2.findContours(
        thresholdedImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    i = 0

    bestContours = []
    # list for storing names of shapes
    for contour in contours:
        (contourX,contourY,contourW,contourH) = cv2.boundingRect(contour)
        # here we are ignoring first counter because
        # findcontour function detects whole image as shape
        if i == 0:
            i = 1
            continue
        i += 1

        x = int(contourX + contourW / 2)
        y = int(contourY + contourH / 2)
        
        if isSquare(contourW, contourH) and isBigEnough(contourW, contourH):
            # putting shape name at center of each shape
            # text = str(i)
            # cv2.putText(image, text, (x, y),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (25, 155, 155), 1)
            # cv2.rectangle(image, (contourX, contourY), (contourX + contourW, contourY + contourH), (0, 0, 0), 1)
            bestContours.append(contour)
            points.append((x,y,contourW,contourH))
            cv2.rectangle(thresholdedImage, (contourX, contourY), (contourX + contourW, contourY + contourH), (125, 125, 125), 2)
        else:
            cv2.rectangle(thresholdedImage, (contourX, contourY), (contourX + contourW, contourY + contourH), (125, 125, 125), 1)

    avgArea = calcAvgArea(points)
    areaGap = 25 # in %

    for i in range(len(points)-1, -1, -1):
        if calcArea(points[i]) > avgArea * (100 + areaGap) / 100 or calcArea(points[i]) < avgArea * (100 - areaGap) / 100:
            cv2.rectangle(thresholdedImage, (points[i][0], points[i][1]), (points[i][0] + points[i][2], points[i][1] + points[i][3]), (0, 255, 0), 1)
            del points[i]
            del bestContours[i]

    if len(points) > 1:
        pointsBox = getPointsBox(points)
        pointsBox = addMargin(pointsBox, 15, image)
        
        if (not pointsBox[1] == pointsBox[3]) and (not pointsBox[0] == pointsBox[2]):
            roi = image[pointsBox[1]:pointsBox[3], pointsBox[0]:pointsBox[2]]
            cv2.imshow("ROI", roi) 
            cv2.imshow("Result", brailleReaderV3.translate(image.copy(), roi, (pointsBox[0], pointsBox[1]), bestContours, mythreshold))
        # drawPointsBox(image, pointsBox)
    
    cv2.imshow("Image", image)
    cv2.imshow("Threshlolded", thresholdedImage)


    key = cv2.waitKey(100)
    if key == ord('q'):
        break
    elif key == ord('t'):
        if mythreshold > 0:
            mythreshold -= 1
    elif key == ord('y'):
        mythreshold += 1
    elif key == ord('g'):
        if sizeThreshold > 0:
            sizeThreshold -= 1
    elif key == ord('h'):
        sizeThreshold += 1
    if key != -1:
        print("Size Threshold (g/h): ", sizeThreshold)
        print("Threshold (t/y) : ", mythreshold)
