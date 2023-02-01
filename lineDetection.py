import cv2
import numpy as np

myGap = 50

cap = cv2.VideoCapture(0)

while True:
    # img = cv2.imread("./res/videoImage.png")
    
    ret, img = cap.read()

    scale_percent = 100 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.putText(img, 'tolerence : ' + str(myGap), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6  , [125, 125, 125])

    edges = cv2.Canny(gray, 75, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 150, minLineLength=200, maxLineGap=myGap)
    
    if isinstance(lines, np.ndarray):
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 128), 3)
        cv2.imshow("linesEdges", edges)
        cv2.imshow("linesDetected", img)

    key = cv2.waitKey(100)
    if key == ord('q'):
        break
    elif key == ord('t'):
        if myGap > 0:
            myGap -= 10
    elif key == ord('y'):
        myGap += 10

cv2.destroyAllWindows()