import cv2
import tkinter as tk

# read image 
image = cv2.imread('res/Q.png', cv2.IMREAD_GRAYSCALE)
print(image.size)
print(image.shape)
(retVal, newImg) = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY)

scale_percent = 600 # percent of original size
width = int(newImg.shape[1] * scale_percent / 100)
height = int(newImg.shape[0] * scale_percent / 100)
dim = (width, height)
  
# resize image
resized = cv2.resize(newImg, dim, interpolation = cv2.INTER_AREA)
print(resized[100, 100])
print(resized.shape)

i = 1
j = 1

h, w = resized.shape

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
            print(1)
        else:
            print(0)

# show the image, provide window name first
cv2.imshow('image window', resized)
# add wait key. window waits until user presses a key
cv2.waitKey(0)
# and finally destroy/close all open windows
cv2.destroyAllWindows()

# brailleTable = {'100000' : 'a', '110000' : 'b', '100100' : 'c',
#                 '100110' : 'd', '100010' : 'e', '110100' : 'f',
#                 '110110' : 'g', '110010' : 'h', '010100' : 'i',
#                 '010110' : 'j', '101000' : 'k', '111000' : 'l',
#                 '101100' : 'm', '101110' : 'n', '101010' : 'o',
#                 '111100' : 'p', '111110' : 'q', '111010' : 'r',
#                 '011100' : 's', '011110' : 't', '101001' : 'u',
#                 '111001' : 'v', '010111' : 'w', '101101' : 'x',
#                 '101111' : 'y', '101011' : 'z'}

# def update():
#     output = ""
#     for button in brailleButtons:
#         if button.state:
#             output += "1"
#         else:
#             output += "0"

#     value = brailleTable.get(output)
    
#     if value:
#         display.configure(text = value)
#     else:
#         display.configure(text = "?")
    
# myWindow = tk.Tk()
# myWindow.title("BrailleTranslate")

# def update():
#     output = ""
#     for button in brailleButtons:
#         if button.state:
#             output += "1"
#         else:
#             output += "0"

#     value = brailleTable.get(output)
    
#     if value:
#         display.configure(text = value)
#     else:
#         display.configure(text = "?")
    
# class brailleButton:
#     def __init__(self, id):
#         self.button = tk.Button(text = str(id), command = self.switchState, width = 10, height = 5)
#         self.state = False
#     def switchState(self):
#         if self.state:
#             self.state = False
#             self.button.configure(relief = tk.RAISED)
#         else:
#             self.state = True
#             self.button.configure(relief = tk.SUNKEN)
#         update()

# brailleButtons = list(brailleButton(i + 1) for i in range(6))
# display = tk.Label(text = "?")

# for col in range(2):
#     for row in range(3):
#         brailleButtons[col * 3 + row].button.grid(column = col, row = row)
# display.grid(column = 0, row = 3, columnspan = 2)
# myWindow.mainloop()
