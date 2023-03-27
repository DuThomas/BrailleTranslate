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

    split_value = 3
    min_value = 0
    max_value = 255
    lower_value = min_value
    upper_value = max_value

    itera = 1
    points_list = [[0], [], [2]]
    points_lens = []
    while not (len(points_list[0])
               == len(points_list[1])
               == len(points_list[2])):
        print("iteration : ", itera)
        print(lower_value, upper_value)
        step_value = int((upper_value-lower_value) / (split_value+1))
        # accuracies = []
        # result_images = []
        thresholded_images = []
        # braille_chars_list = []
        points_list = []
        for i in range(split_value):
            threshold_value = lower_value + (i+1)*step_value
            print("th", threshold_value, end=' ')

            image = video_image.copy()
            thresholded_images.append(roiFinder.threshold_image(
                                                        image,
                                                        threshold_value))
            points_list.append(roiFinder.get_points(image, thresholded_images[i]))
        
        new_points_lens = list(len(points) for points in points_list)
        if new_points_lens != points_lens:
            points_lens = new_points_lens.copy()
        else:
            break
        print(points_lens)
        itera += 1
        if points_lens[0] >= points_lens[1] and points_lens[0] > points_lens[2]:
            upper_value -= step_value
        elif points_lens[2] >= points_lens[1] and points_lens[2] > points_lens[0]:
            lower_value += step_value
        else:
            upper_value -= int(0.5 * step_value)
            lower_value += int(0.5 * step_value)
    
    threshold_value -= step_value
    print(threshold_value)
    image = video_image.copy()
    result_image = image.copy()
    thresholded_image = roiFinder.threshold_image(
                                                image,
                                                threshold_value)
    braille_chars = brailleReader.get_braille_chars(
                                                image,
                                                result_image,
                                                thresholded_image)

    roiFinder.display_translations(result_image
                                   , braille_chars)
    cv2.putText(result_image, "threshold : " + str(threshold_value)
                , (5, 40), cv2.FONT_HERSHEY_SIMPLEX
                , 0.6, (100, 100, 100), 2)

    display_fps(result_image, start_time)
    
    cv2.imshow("Input", thresholded_image)
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
        