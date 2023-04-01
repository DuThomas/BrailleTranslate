import cv2, argparse, time
import src.roiFinderV3debug as roiFinder
import src.brailleReaderV3debug  as brailleReader


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


def diplay_threshold(image, threshold_value): 
    cv2.putText(image, "threshold : " + str(int(threshold_value))
                , (3, 38), cv2.FONT_HERSHEY_SIMPLEX
                , 0.6, (230, 230, 230), 2)
    cv2.putText(image, "threshold : " + str(int(threshold_value))
                , (5, 40), cv2.FONT_HERSHEY_SIMPLEX
                , 0.6, (100, 100, 100), 2)


parser = argparse.ArgumentParser(usage="%(prog)s <image_path> -h for help")
parser.add_argument('-d', '--debug', action='store_true')
args = parser.parse_args()

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
            points_list.append(roiFinder.get_points(thresholded_images[i], True))
        
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
    debug_img = thresholded_image.copy()
    braille_chars = brailleReader.get_braille_chars(image,
                                                    debug_img,
                                                    True)

    roiFinder.display_translations(result_image
                                   , braille_chars)

    roiFinder.translate_braille_chars(thresholded_image, braille_chars)
    roiFinder.display_translations(result_image, braille_chars)
    diplay_threshold(result_image, threshold_value)
    display_fps(result_image, start_time)
    
    if args.debug:
        cv2.imshow("Input", video_image)
        cv2.imshow("Debug", debug_img)
    else:
        cv2.imshow("Thresh", thresholded_image)
    cv2.imshow("Result", result_image)

    key = cv2.waitKey(100)
    if key == ord('q'):
        break
        