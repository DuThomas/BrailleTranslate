import cv2
from math import *
import translator
import brailleReaderV3debug as brailleReaderV3
from src.utils import *
        
def isSquare(point):
    gap = 20 # in %
    #print(str(height * 100 / 120) + " - - " + str(width) + " - - " + str(height * 100 / 80))
    return point.height * 100 / (100 + gap) < point.width < point.height * 100 / (100 - gap)

def isBigEnough(point):
    minLenght = 7
    return point.width > minLenght and point.height > minLenght

def hasAvgArea(point, avgArea):
    areaGap = 25 # in %
    return (avgArea * (100 - areaGap) / 100 < calcArea(point) < avgArea * (100 - areaGap) / 100)

def hasAvgSize(point, avgSize):
    sizeGap = 20 # in %
    correctWidth = (avgSize[0] * (100 - sizeGap) / 100 < point.width < avgSize[0] * (100 + sizeGap) / 100)
    correctHeight = (avgSize[1] * (100 - sizeGap) / 100 < point.width < avgSize[1] * (100 + sizeGap) / 100)
    return correctWidth and correctHeight

def drawPointsBox(image, box):
    if isinstance(box, tuple):
        cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 0, 0), 3)

def getPointsBox(points):
    if len(points) > 0:
        xMin = points[0].x
        xMax = points[0].x
        yMin = points[0].y
        yMax = points[0].y
        for point in points:
            #cv2.rectangle(image, ((int)(point[0] - point[2] / 2), (int)(point[1] - point[3] / 2)),
            #((int)(point[0] + point[2] / 2), (int)(point[1] + point[3] / 2)), (0, 0, 0), 1)
            if point.x + point.width > xMax:
                xMax = point.x + point.width
            if point.x < xMin:
                xMin = point.x
            if point.y + point.height > yMax:
                yMax = point.y + point.height
            if point.y < yMin:
                yMin = point.y
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
    """  return the air of a point """
    return point.width * point.height

def calcAvgArea(points):
    if len(points) > 0:
        area = 0 
        for point in points:
            area += calcArea(point)
        return area / len(points)

def calcAreaVariance(points, avgArea):
    v = 0
    n = len(points)
    for point in points:
        v += calcArea(point)**2
    v = v / n - avgArea**2
    return v
        
def calcAvgSize(points):
    widthSum = 0
    heightSum = 0
    nbPoint = len(points)
    for point in points:
        widthSum += point.width
        heightSum += point.height
    
    avgWidth = widthSum / nbPoint
    avgHeight = heightSum / nbPoint
    return (avgWidth, avgHeight)

def acsSortByArea(points):
    for i in range(1, len(points)):
        key_item = points[i]
        j = i - 1
        while j >= 0 and calcArea(points[j]) > calcArea(key_item):
            points[j + 1] = points[j]
            j -= 1
        points[j + 1] = key_item
    return points

# converting image into grayscale image

cap = cv2.VideoCapture(0)
image0 = cv2.imread('./res/videoImage.png')

# converting image into grayscale image
gray0 = cv2.cvtColor(image0, cv2.COLOR_BGR2GRAY)

sizeThreshold = 120
mythreshold = 115

while True:
    points = []
    # ret, image = cap.read()
    image = cv2.imread('./res/videoImage.png')
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #gray = gray0.copy()
    #image = image0.copy()
    
    _, thresholdedImage = cv2.threshold(gray, mythreshold, 255, cv2.THRESH_BINARY)

    # using a findContours() function
    contours, _ = cv2.findContours(
        thresholdedImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    points = list(brailleReaderV3.Point(contour) for contour in contours)
    bestPoints = []

    if len(points) > 1: 
        i = 0
        for point in points:
            if i == 0:
                i = 1
                continue
            
            if isSquare(point) and isBigEnough(point):
                point.id = i
                bestPoints.append(point)
                point.frame(thresholdedImage, 1, (200, 200, 200), 2)
            else:
                point.frame(thresholdedImage, 1, (125, 125, 125), 1)
            i += 1
        avgArea = calcAvgArea(bestPoints)
        avgSize = calcAvgSize(bestPoints)
        # print(calcAreaVariance(points, avgArea))
        print(avgArea)

    acsSortByArea(bestPoints)

    while calcAreaVariance(bestPoints, avgArea) > 50:
        # print("a")
        # avgArea = calcAvgArea(bestPoints)
        # print(len(bestPoints))
        # print(avgArea)
        # input()
        if abs(calcArea(bestPoints[-1]) - avgArea) > abs(calcArea(bestPoints[0]) - avgArea):
            bestPoints[-1].circle(thresholdedImage, (111, 111, 111), 2)
            del bestPoints[-1]
        else:
            bestPoints[0].circle(thresholdedImage, (111, 111, 111), 2)
            del bestPoints[0]
        
        avgArea = calcAvgArea(bestPoints)
    
    # for point in bestPoints.copy():
    #     print(calcArea(point))
    #     if not hasAvgArea(point, avgArea):
    #         # point.frame(thresholdedImage, 1, (111, 111, 111), 2)
    #         point.circle(thresholdedImage, (111, 111, 111), 2)
    #         # del points[i]
    #         bestPoints.remove(point)
        

    if len(bestPoints) > 1:
        pointsBox = getPointsBox(bestPoints)
        pointsBox = addMargin(pointsBox, 15, image)
        
        if (not pointsBox[1] == pointsBox[3]) and (not pointsBox[0] == pointsBox[2]):
            roi = image[pointsBox[1]:pointsBox[3], pointsBox[0]:pointsBox[2]]
            cv2.imshow("ROI", roi) 
            cv2.imshow("Result", brailleReaderV3.translate(image.copy(), roi, (pointsBox[0], pointsBox[1]), bestPoints, mythreshold))
        # drawPointsBox(image, pointsBox)
        for i in range(len(bestPoints)):
            bestPoints[i].id = i
            bestPoints[i].displayId(image, (55, 55, 55), 2)
            print(i, " : ", calcArea(bestPoints[i]), avgArea)
    

    cv2.imshow("Image", image)
    cv2.imshow("Threshlolded", thresholdedImage)


    key = cv2.waitKey(0)
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
