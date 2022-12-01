import cv2
import numpy as np
import writechar

def newImage(width, height, bgColor):
    image = np.zeros((width, height , 3), np.uint8)
    for row in range(height):
        for col in range(width):
            image[col, row] = bgColor
    return image
            
white = [255, 255, 255]
black = [0, 0, 0]

width = 400
height = 500
image = newImage(width, height, white)

x = 50
y = 20

writechar.writeBrailleText(image, (y, x), black)

cv2.destroyAllWindows()
cv2.imwrite("./res/allChar2.png", image)
