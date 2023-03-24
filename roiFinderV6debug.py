import cv2
from math import *
import translator
import brailleReaderV6debug  as brailleReader
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
            xMin = min(xMin, point.x)
            xMax = max(xMax, point.x + point.width)
            yMin = min(yMin, point.y)
            yMax = max(yMax, point.y + point.height)

        return (xMin, yMin, xMax, yMax)
    else:
        print("dddd")

def addMargin(box, margin, image):
    h, w, _ = image.shape
    xMin, yMin, xMax, yMax = box[0], box[1], box[2], box[3]

    xMin = max(0, xMin - margin)
    yMin = max(0, yMin - margin)
    xMax = min(w - 1, xMax + margin)
    yMax = min(h - 1, yMax + margin)

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


def find_valid_points(points, image):
    count = 1
    best_points = []
    for point in points[1:]: # skip first point which is the entire frame
        if isSquare(point) and isBigEnough(point):
            point.id = count
            bestPoints.append(point)
            point.draw_frame(image, 0, (200, 200, 200), 2)
        else:
            point.draw_frame(image, 0, (125, 125, 125), 1)
        count += 1
    return bestPoints


def remove_big_points(points):
    avgArea = calcAvgArea(points)
    while calcAreaVariance(points, avgArea) > 1000:
        if abs(calcArea(points[-1]) - avgArea) > abs(calcArea(points[0]) - avgArea):
            pointIndex = -1
        else:
            pointIndex = 0

        points[pointIndex].draw_circle(thresholdedImage, (111, 111, 111), 2)
        del points[pointIndex]

        avgArea = calcAvgArea(points)

def display_points_id(image, points):
    for i in range(len(points)):
            points[i].id = i
            points[i].displayId(image, (55, 55, 55), 2)
# converting image into grayscale image

cap = cv2.VideoCapture(0)
image0 = cv2.imread('./res/videoImage.png')

# converting image into grayscale image
gray0 = cv2.cvtColor(image0, cv2.COLOR_BGR2GRAY)

sizeThreshold = 120
mythreshold = 115

while True:
    ret, image = cap.read()
    # image = cv2.imread('./res/videoImage.png')
    if not ret:
        continue
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #gray = gray0.copy()
    #image = image0.copy()
    
    _, thresholdedImage = cv2.threshold(gray, mythreshold, 255, cv2.THRESH_BINARY)

    # using a findContours() functioncircle
    contours, _ = cv2.findContours(
        thresholdedImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    points = list(brailleReader.Point(contour) for contour in contours)
    bestPoints = []

    if len(points) > 1: 
        bestPoints = find_valid_points(points, thresholdedImage)

    acsSortByArea(bestPoints)

    if len(bestPoints) > 1:
        remove_big_points(bestPoints)

        pointsBox = getPointsBox(bestPoints)
        # print("->", pointsBox, image.shape, (pointsBox[2] - pointsBox[0], pointsBox[3] - pointsBox[1]))
        pointsBox = addMargin(pointsBox, 15, image)
        
        if (not pointsBox[1] == pointsBox[3]) and (not pointsBox[0] == pointsBox[2]) or True:
            roi = image.copy()
            roi = roi[pointsBox[1]:pointsBox[3], pointsBox[0]:pointsBox[2]]
            # print(pointsBox, image.shape, (pointsBox[2] - pointsBox[0], pointsBox[3] - pointsBox[1]))
            cv2.imshow("ROI", roi) 
            
            braille_chars = brailleReader.translate(image, bestPoints)
            for braille_char in braille_chars:
                brailleReader.display_boxes(image, braille_chars)


            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            # setting threshold of gray image
            _, threshold = cv2.threshold(gray, mythreshold, 255, cv2.THRESH_BINARY)
            
            cv2.imshow("Thresholded ROI", threshold)

            for i in range(len(braille_chars)):
                tlCorner2 = coordToInt((braille_chars[i].x, braille_chars[i].y))
                brCorner2 = (tlCorner2[0] + int(braille_chars[i].width), tlCorner2[1] + int(braille_chars[i].height))
                tlCorner = (tlCorner2[0] - pointsBox[0], tlCorner2[1] - pointsBox[1])
                brailleChar = threshold[tlCorner[1]:tlCorner[1] + int(braille_chars[i].height), tlCorner[0]:tlCorner[0] + int(braille_chars[i].width)]

                traslation = translator.translate(brailleChar)
                cv2.putText(image, traslation, brCorner2, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
                cv2.rectangle(image, tlCorner2, brCorner2, [0, 0, 255])


            cv2.imshow("Result", image)

        # drawPointsBox(image, pointsBox)
        display_points_id(image, bestPoints)
            # print(i, " : ", calcArea(bestPoints[i]), avgArea)
    
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
