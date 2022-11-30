import cv2
import numpy as np
from matplotlib import pyplot as plt



mythreshold = 189
erode = 0
dilate = 0
while True:
    xDistances = []
    yDistances = []
    xTuples = []
    yTuples = []
    # reading image
    # img = cv2.imread('./res/Test.png')
    img = cv2.imread('./allChar.png')

    scale_percent = 300 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    # converting image into grayscale image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # setting threshold of gray image
    _, threshold = cv2.threshold(gray, mythreshold, 255, cv2.THRESH_BINARY)

    threshold = cv2.erode(threshold, None, iterations=erode)
    threshold = cv2.dilate(threshold, None, iterations=dilate)

    # using a findContours() function
    contours, _ = cv2.findContours(
        threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    i = 0

    # list for storing names of shapes
    for contour in contours:
        j = 0
        # here we are ignoring first counter because
        # findcontour function detects whole image as shape
        if i == 0:
            i = 1
            continue
        i += 1
        # cv2.approxPloyDP() function to approximate the shape
        approx = cv2.approxPolyDP(
            contour, 0.01 * cv2.arcLength(contour, True), True)
        
        # using drawContours() function
        cv2.drawContours(img, [contour], 0, (0, 0, 255), 5)

        # finding center point of shape
        M = cv2.moments(contour)
        if M['m00'] != 0.0:
            x = int(M['m10']/M['m00'])
            y = int(M['m01']/M['m00'])

        for contour2 in contours:
            if j == 0:
                j = 1
                continue
            j += 1
            # finding center point of shape
            M2 = cv2.moments(contour2)
            if M2['m00'] != 0.0:
                x2 = int(M2['m10']/M2['m00'])
                y2 = int(M2['m01']/M2['m00'])
            xDistance = (x - x2)
            yDistance = (y - y2)
            if(xDistance != 0 and abs(xDistance) not in xDistances):
                xDistances.append(abs(xDistance))
                xTuples.append(((abs(xDistance), i, j)))
                # cv2.line(img, (x, y), (x - xDistance, y), [255, 0, 0])
                cv2.line(img, (x, y), (x2 , y2), [255, 0, 0])
            if(yDistance != 0 and abs(yDistance) not in yDistances):
                yDistances.append(abs(yDistance))
                yTuples.append(((abs(yDistance), i, j)))
                cv2.line(img, (x, y), (x2 , y2), [0, 0, 255])
                # cv2.line(img, (x, y), (x, y - yDistance), [255, 0, 0])

        print(i, " : ", x, y)

        # putting shape name at center of each shape
        if len(approx) == 3:
            cv2.putText(img, 'Triangle', (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        elif len(approx) == 4:
            cv2.putText(img, 'Quadrilateral', (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        elif len(approx) == 5:
            cv2.putText(img, 'Pentagon', (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        elif len(approx) == 6:
            cv2.putText(img, 'Hexagon', (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        else:
            text = 'circle'+str(i)
            cv2.putText(img, text, (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # displaying the image after drawing contours
    cv2.imshow('shapes', img)
    cv2.imshow('gray', threshold)


    key = cv2.waitKey(0)
    if key == ord('q'):
        break
    elif key == ord('t'):
        if mythreshold > 0:
            mythreshold -= 1
    elif key == ord('y'):
        mythreshold += 1
    elif key == ord('g'):
        if erode > 0:
            erode -= 1
    elif key == ord('h'):
        erode += 1
    elif key == ord('v'):
        if dilate > 0:
            dilate -= 1
    elif key == ord('b'):
        dilate += 1
    print("threshold : ", mythreshold)
    print("erode : ", erode)
    print("dilate : ", dilate)
    print(xDistances, yDistances)
    print(xTuples, yTuples)

cv2.destroyAllWindows()

# var = "011110"
# for i in range(len(var)):
#     if(var[i] == '1'):
#         img[tlcorner[0] + i3 * 2][tlCorner[1] + i//3 * 2] = [255, 255, 255]

