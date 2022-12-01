import cv2
import numpy as np
import translator

mythreshold = 189
erode = 0
dilate = 0
while True:
    img = cv2.imread('./res/Test.png')
    # img = cv2.imread('./res/brailleTextePhoto.png')

    scale_percent = 800 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    # converting image into grayscale image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # setting threshold of gray image
    _, threshold = cv2.threshold(gray, mythreshold, 255, cv2.THRESH_BINARY)

    # Taking a matrix of size 5 as the kernel
    # kernel = np.ones((5, 5), np.uint8)
    
    outPut = cv2.erode(threshold, None, iterations=erode)
    outPut = cv2.dilate(outPut, None, iterations=dilate)

    # The first parameter is the original image,
    # kernel is the matrix with which image is
    # convolved and third parameter is the number
    # of iterations, which will determine how much
    # you want to erode/dilate a given image.
    img_erosion = cv2.erode(threshold, None, iterations=erode)
    img_dilation = cv2.dilate(threshold, None, iterations=dilate)
    
    cv2.imshow('Input', img)
    cv2.imshow('Erosion', img_erosion)
    cv2.imshow('Dilation', img_dilation)
    cv2.imshow('Gray', threshold)
    cv2.imshow('OutPut', outPut)

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
    elif key == ord('s'):
        cv2.imwrite("./res/processedImage.png", outPut)

    print("threshold : ", mythreshold)
    print("erode : ", erode)
    print("dilate : ", dilate)
    print(translator.translate(outPut))

cv2.destroyAllWindows()