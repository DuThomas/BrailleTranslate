import cv2
import sys
import brailleTable

# read image 
image = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
(retVal, newImg) = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY)

scale_percent = 600 # percent of original size
width = int(newImg.shape[1] * scale_percent / 100)
height = int(newImg.shape[0] * scale_percent / 100)
dim = (width, height)

# resize image
resized = cv2.resize(newImg, dim, interpolation = cv2.INTER_AREA)

i = 1
j = 1

h, w = resized.shape

caractere = []

for col in range(2):
    i = int(col * w/2)
    for row in range(3):
        j = int(row * h/3)
        while (i < (col + 1) * w/2 and j < (row + 1) * h/3 and resized[j, i] != 0):
            i += 1
            if(i == int((col + 1) * w/2)):
                i = int(col * w/2)
                j += 1
        if(i < (col + 1) * w/2 and j < (row + 1) * h/3):
            caractere.append(1)
        else:
            caractere.append(0)

output = ""
for i in caractere:
    output += str(i);

value = brailleTable.brailleTable.get(output)
    
if value:
    print(value)
else:
    print("?")

# # show the image, provide window name first
# cv2.imshow('image window', resized)
# # add wait key. window waits until user presses a key
# cv2.waitKey(0)
# # and finally destroy/close all open windows
# cv2.destroyAllWindows()