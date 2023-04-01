import cv2, argparse, os
from src import(brailleReaderV3debug,
                roiFinderV3debug,
                brailleConstants as brCst)
import argparse
import numpy as np
import time


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


def is_image(image_path):
    if not os.path.isfile(image_path):
        raise argparse.ArgumentTypeError('Cannot open "{}"'.format(image_path))
    elif image_path.split('.')[-1] not in ['jpg', 'JPG', 'png']:
        raise argparse.ArgumentTypeError('"{}" file format is not accepted'.format(image_path))
    return image_path


parser = argparse.ArgumentParser(usage="%(prog)s <image_path> -h for help")
parser.add_argument('-d', '--debug', action='store_true')
parser.add_argument('image_path', type=is_image)
args = parser.parse_args()

img = cv2.imread(args.image_path)
# img = brailleReader.zoom(img, 50)

while True:
    start_time = time.time()
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

            image = img.copy()
            thresholded_images.append(roiFinderV3debug.threshold_image(
                                                        image,
                                                        threshold_value))
            points_list.append(roiFinderV3debug.get_points(thresholded_images[i], args.debug))

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
        elif points_lens[1] > points_lens[0] and points_lens[1] > points_lens[2]:
            upper_value -= int(0.5 * step_value)
            lower_value += int(0.5 * step_value)
        else:
            print("error")

    threshold_value -= step_value
    print(threshold_value)
    image = img.copy()
    result_image = image.copy()

    thresholded_image = roiFinderV3debug.threshold_image(image,
                                                         threshold_value)
    debug_img = thresholded_image.copy()
    braille_chars = brailleReaderV3debug.get_braille_chars(image,
                                                           debug_img,
                                                           args.debug)
    
    roiFinderV3debug.translate_braille_chars(thresholded_image, braille_chars)
    roiFinderV3debug.display_translations(result_image, braille_chars)
    cv2.putText(result_image, "threshold : " + str(threshold_value), (5, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)

    cv2.imshow("Result" + str(i), cat_images(result_image, debug_img))

    print(time.time()-start_time)
    key = cv2.waitKey(0)
    if key == ord('q'):
        break
        