import cv2
import translator

def findBox(image):
    h, w= image.shape
    xmin = w - 1
    ymin = h - 1
    xmax = 0
    ymax = 0

    for lig in range(h):
        for col in range(w):
            if(image[lig, col] == 0):
                if(lig > ymax):                
                    ymax = lig
                if(lig < ymin):               
                    ymin = lig
                if(col > xmax):               
                    xmax = col
                if(col < xmin):              
                    xmin = col
    return (xmin, ymin, xmax, ymax)

image = cv2.imread('./res/brailleText.png')

scale_percent = 200 # percent of original size
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

textBox = findBox(threshold)

xDistances = []
yDistances = []

# using a findContours() function
contours, _ = cv2.findContours(
    threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

i = 0

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

    j = 0

    for contour2 in contours:
        (contour2X, contour2Y, contour2W, contour2H) = cv2.boundingRect(contour2)
        if j == 0:
            j = 1
            continue
        j += 1

        x2 = int(contour2X + contour2W / 2)
        y2 = int(contour2Y + contour2H / 2)

        xDistance = (x - x2)
        yDistance = (y - y2)

        if(xDistance != 0 and abs(xDistance) not in xDistances):
            xDistances.append(abs(xDistance))
            cv2.line(image, (x, y), (x2 , y2), [255, 0, 0])

        if(yDistance != 0 and abs(yDistance) not in yDistances):
            yDistances.append(abs(yDistance))
            cv2.line(image, (x, y), (x2 , y2), [0, 0, 255])

    # putting shape name at center of each shape
    text = str(i)
    cv2.putText(image, text, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (25, 155, 155), 2)

cv2.rectangle(image,(textBox[0]-1,textBox[1]-1),(textBox[2]+1,textBox[3]+1),(100,100,100),1)
cv2.rectangle(threshold,(textBox[0]-1,textBox[1]-1),(textBox[2]+1,textBox[3]+1),(100, 100, 100),1)

xDistances.sort()
yDistances.sort()

rectW = int(2.5 * xDistances[0])
rectH = int(3.5 * yDistances[0])

row = textBox[1]

while row < textBox[3]:
    col = textBox[0]
    while col < textBox[2]:
        brailleChar = threshold[row:row + int(2.5 * yDistances[0]), col:col + int(1.5 * xDistances[0])]
        cv2.putText(threshold, translator.translate(brailleChar), (col + int(1.5 * xDistances[0] / 2), row + int(2.5 * yDistances[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
        cv2.rectangle(threshold, (col, row), (col + int(1.5 * xDistances[0]), row + int(2.5 * yDistances[0])), [0, 0, 255])
        col += rectW
    row += rectH

cv2.imshow('shapes', image)
cv2.imshow('output', threshold)
cv2.imwrite("./res/output.png", threshold)

cv2.waitKey(0)
cv2.destroyAllWindows()
