import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, img = cap.read()

    cv2.imshow('Input', img)

    key = cv2.waitKey(100)
    if key == ord('q'):
        break
    elif key == ord('s'):
        cv2.imwrite("./res/videoImage.png", img)

cv2.destroyAllWindows()