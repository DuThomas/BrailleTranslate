import cv2
import src.roiFinderV3debug as roiFinder
import src.brailleReaderV3debug as brailleReader
import sys

threshold_value = roiFinder.DEFAULT_THRESHOLD
size_threshold = roiFinder.size_threshold

if len(sys.argv) == 1:
    print("Please precise path of image")
    exit(1)

image_path = sys.argv[1]
img = cv2.imread(image_path)
# img = brailleReader.zoom(img, 50)

while True:
    if img.size == 0:
        print("Cannot open ", image_path)
        exit(1)
    
    image = img.copy()
    result_image = image.copy()
    thresholded_image = roiFinder.threshold_image(
                                                image,
                                                threshold_value)
    th = thresholded_image.copy()

    braille_chars = brailleReader.get_braille_chars(
                                                image,
                                                result_image,
                                                thresholded_image)

    roiFinder.display_translations(result_image, braille_chars)
    

    cv2.putText(result_image, "threshold : " + str(int(threshold_value))
                , (5, 40), cv2.FONT_HERSHEY_SIMPLEX
                , 0.6, (100, 100, 100), 2)
    
    cv2.imshow("Thresh", thresholded_image)
    cv2.imshow("Result", result_image)

    key = cv2.waitKey(0)
    if key == ord('q'):
        break
    elif key == ord('t'):
        if threshold_value > 0:
            threshold_value -= 1
    elif key == ord('y') and threshold_value < 255:
        threshold_value += 1
    elif key == ord('g'):
        if size_threshold > 0:
            size_threshold -= 1
    elif key == ord('h'):
        size_threshold += 1
    if key != -1:
        print("Size Threshold (g/h): ", size_threshold)
        