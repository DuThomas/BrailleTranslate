import cv2, argparse, time
from src import(brailleReaderV3,
                roiFinderV3,
                brailleConstants as brCst)


def diplay_threshold(image, threshold_value): 
    cv2.putText(image, "threshold : " + str(int(threshold_value))
                , (3, 38), cv2.FONT_HERSHEY_SIMPLEX
                , 0.6, (230, 230, 230), 2)
    cv2.putText(image, "threshold : " + str(int(threshold_value))
                , (5, 40), cv2.FONT_HERSHEY_SIMPLEX
                , 0.6, (100, 100, 100), 2)


def display_fps(image, start_time):
    fps = 1 / (time.time()-start_time)
    cv2.putText(image, "fps : " + str(int(fps)), (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
    

parser = argparse.ArgumentParser(usage="%(prog)s <image_path> -h for help")
parser.add_argument('-a', '--auto', action='store_true',
                    help='auto-thresholding')
parser.add_argument('-d', '--debug', action='store_true',
                    help='show widows with more informations')
args = parser.parse_args()

cap = cv2.VideoCapture(0)

while True:
    start_time = time.time()
    ret, video_image = cap.read()
    if not ret:
        print("Cannot read camera")
        exit(1)
    threshold_value = (brailleReaderV3.find_best_threshold(video_image)
                       if args.auto
                       else brCst.DEFAULT_THRESHOLD)
    result_image = video_image.copy()
    thresholded_image = roiFinderV3.threshold_image(video_image,
                                                         threshold_value)
    debug_img = thresholded_image.copy()

    braille_chars = brailleReaderV3.get_braille_chars(video_image,
                                                           debug_img,
                                                           args.debug)
    
    roiFinderV3.translate_braille_chars(thresholded_image, braille_chars)
    roiFinderV3.display_translations(result_image, braille_chars)
    diplay_threshold(result_image, threshold_value)
    
    if args.debug:
        cv2.imshow("Input", video_image)
        cv2.imshow("Debug", debug_img)
    else:
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
        