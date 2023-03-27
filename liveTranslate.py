import cv2
import src.roiFinderV3debug as roiFinder
import time
import src.brailleReaderV3debug  as brailleReader

def display_fps(image, start_time):
    fps = 1 / (time.time()-start_time)
    cv2.putText(image, "fps : " + str(int(fps)), (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)


threshold_value = roiFinder.DEFAULT_THRESHOLD
size_threshold = roiFinder.size_threshold

cap = cv2.VideoCapture(0)
while True:
    start_time = time.time()
    ret, video_image = cap.read()
    if not ret:
        print("Cannot read camera")
        continue
    result_image = video_image.copy()
    thresholded_image = roiFinder.threshold_image(
                                                video_image,
                                                threshold_value)

    braille_chars = brailleReader.get_braille_chars(
                                                video_image,
                                                result_image,
                                                thresholded_image)

    roiFinder.display_translations(result_image, braille_chars)
    

    display_fps(result_image, start_time)
    cv2.putText(result_image, "threshold : " + str(int(threshold_value))
                , (5, 40), cv2.FONT_HERSHEY_SIMPLEX
                , 0.6, (100, 100, 100), 2)
    
    cv2.imshow("Thresh", thresholded_image)
    cv2.imshow("Result", result_image)

    key = cv2.waitKey(100)
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
        