import cv2
import src.roiFinderV3 as roiFinder
import time
import src.brailleReaderV3  as brailleReader

def display_fps(image, start_time):
    fps = 1 / (time.time()-start_time)
    cv2.putText(image, "fps : " + str(int(fps)), (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)

def braille_chars_score(braille_chars, threshold_value):
    # print(threshold_value, end='    ')
    unknown_count = 0
    for braille_char in braille_chars:
        if braille_char.translation in ['?',' ']:
            unknown_count += 1
        # print("({}) ".format(braille_char.translation), end='')
    # print('{}/{} = {}'.format(unknown_count, len(braille_chars), unknown_count/len(braille_chars)))
    # print()
    if braille_chars:
        return(unknown_count/len(braille_chars))
    else:
        return 1


threshold_value = roiFinder.DEFAULT_THRESHOLD
size_threshold = roiFinder.size_threshold

cap = cv2.VideoCapture(0)
while True:
    start_time = time.time()
    ret, video_image = cap.read()
    if not ret:
        print("Cannot read camera")
        continue

    split_value = 4
    max_value = 255
    step_value = int(max_value / (split_value+1))
    scores = []
    result_images = []
    thresholded_images = []
    braille_chars_list = []
    for i in range(split_value):
        threshold_value = (i+1) * step_value

        image = video_image.copy()
        result_images.append(image.copy())
        thresholded_images.append(roiFinder.threshold_image(
                                                    image,
                                                    threshold_value))

        braille_chars_list.append(brailleReader.get_braille_chars(
                                                    image,
                                                    result_images[i],
                                                    thresholded_images[i]))
        
        scores.append(braille_chars_score(braille_chars_list[i]
                                          , threshold_value))

    i = scores.index(min(scores))
    threshold_value = (i+1) * step_value
    roiFinder.display_translations(result_images[i]
                                   , braille_chars_list[i])
    cv2.putText(result_images[i], "threshold : " + str(threshold_value)
                , (5, 40), cv2.FONT_HERSHEY_SIMPLEX
                , 0.6, (100, 100, 100), 2)

    display_fps(result_images[i], start_time)
    
    cv2.imshow("Input", thresholded_images[i])
    cv2.imshow("Result", result_images[i])

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
        