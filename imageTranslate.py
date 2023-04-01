import cv2, argparse, os
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


def is_image(image_path):
    if not os.path.isfile(image_path):
        raise argparse.ArgumentTypeError('Cannot open "{}"'.format(image_path))
    elif image_path.split('.')[-1] not in ['jpg', 'JPG', 'png']:
        raise argparse.ArgumentTypeError('"{}" file format is not accepted'.format(image_path))
    return image_path


parser = argparse.ArgumentParser(usage="%(prog)s <image_path> -h for help")
parser.add_argument('-a', '--auto', action='store_true',
                    help='auto-thresholding')
parser.add_argument('-d', '--debug', action='store_true',
                    help='show widows with more informations')
parser.add_argument('image_path', type=is_image)
args = parser.parse_args()

img = cv2.imread(args.image_path)
threshold_value = (brailleReaderV3.find_best_threshold(img) if args.auto
                   else brCst.DEFAULT_THRESHOLD)

while True:
    input_img = img.copy()
    result_image = input_img.copy()
    thresholded_image = roiFinderV3.threshold_image(input_img,
                                                         threshold_value)
    debug_img = thresholded_image.copy()

    braille_chars = brailleReaderV3.get_braille_chars(input_img,
                                                           debug_img,
                                                           args.debug)
    
    roiFinderV3.translate_braille_chars(thresholded_image, braille_chars)
    roiFinderV3.display_translations(result_image, braille_chars)
    diplay_threshold(result_image, threshold_value)
    
    if args.debug:
        cv2.imshow("Input", input_img)
        cv2.imshow("Debug", debug_img)
    else:
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
        