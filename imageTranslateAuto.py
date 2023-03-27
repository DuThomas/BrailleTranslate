import cv2
import src.roiFinderV3debug as roiFinder
import src.brailleReaderV3debug  as brailleReader
import sys
import numpy as np
import time

threshold_value = roiFinder.DEFAULT_THRESHOLD
size_threshold = roiFinder.size_threshold


def braille_chars_accruracy(braille_chars, threshold_value):
    print(threshold_value, end=' ')
    unknown_count = 0
    for braille_char in braille_chars:
        if braille_char.translation in ['?',' ']:
            unknown_count += 1
    
    if braille_chars:
        accuracy = 1 - unknown_count/len(braille_chars)
        print('{}/{} : {}'.format(unknown_count, len(braille_chars), 1 - unknown_count/len(braille_chars)))
    else:
        print("no points")
        accuracy = 0

    return accuracy


def cat_images(image1, image2):
    h1, w1, _ = image1.shape
    h2, w2 = image2.shape
    if h1 == h2:
        cat_image = np.zeros((h1, w1 + w2, 3), np.uint8)
        cat_image[:h1, :w1] = image1
        for row in range(h1):
            for col in range(w2):
                val = image2[row][col]
                cat_image[row][w1 + col] = [val, val, val]
                
    return cat_image


if len(sys.argv) == 1:
    print("Please precise path of image")
    exit(1)

image_path = sys.argv[1]
img = cv2.imread(image_path)
while True:
    start_time = time.time()
    if img.size == 0:
        print("Cannot open ", image_path)
        exit(1)
    
    split_value = 3
    min_value = 0
    max_value = 255
    lower_value = min_value
    upper_value = max_value

    itera = 1
    points_list = [[0], [], [2]]
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

            image = img.copy()
            thresholded_images.append(roiFinder.threshold_image(
                                                        image,
                                                        threshold_value))
            points_list.append(roiFinder.get_points(image, thresholded_images[i]))
        points_lens = list(len(points) for points in points_list)
        print(points_lens)
        itera += 1
        if points_lens[0] >= points_lens[1] and points_lens[0] > points_lens[2]:
            upper_value -= step_value
        elif points_lens[2] >= points_lens[1] and points_lens[2] > points_lens[0]:
            lower_value += step_value
        elif points_lens[1] > points_lens[0] and points_lens[1] > points_lens[2]:
            upper_value -= int(0.5 * step_value)
            lower_value += int(0.5 * step_value)
        else:
            print("error")

    # i = accuracies.index(min(accuracies))
    i = points_lens.index(max(points_lens))
    threshold_value -= step_value
    print(threshold_value)
    image = img.copy()
    result_image = image.copy()
    thresholded_image = roiFinder.threshold_image(
                                                image,
                                                threshold_value)
    braille_chars = brailleReader.get_braille_chars(
                                                image,
                                                result_image,
                                                thresholded_image)
    # threshold_value = (i+1) * step_value
    roiFinder.display_translations(result_image
                                , braille_chars)
    cv2.putText(result_image, "threshold : " + str(threshold_value)
                , (5, 40), cv2.FONT_HERSHEY_SIMPLEX
                , 0.6, (100, 100, 100), 2)
    
    # cv2.imshow("Input" + str(i), thresholded_images[i])
    # cv2.imshow("Input2" + str(i), result_images[i])
    cv2.imshow("Result" + str(i), cat_images(result_image
                                                , thresholded_image))

    print(time.time()-start_time)
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
        