import cv2
from math import *
from . import translator
from . import brailleReaderV3debug  as brailleReader
from .utils import *

size_threshold = 120
DEFAULT_THRESHOLD = 115

def is_square(point):
    gap = 20 # in %

    return (point.height * 100 / (100+gap)
            < point.width
            < point.height * 100 / (100-gap))


def is_big_enough(point):
    min_lenght = 7
    return point.width > min_lenght and point.height > min_lenght


def is_too_big(point, img_w, img_h):
    return point.width * 3 > img_w  and point.height * 5 > img_h


def has_avg_area(point, avg_area):
    areaGap = 25 # in %
    return (avg_area * (100-areaGap) / 100
            < calc_area(point)
            < avg_area * (100-areaGap) / 100)


def has_avg_size(point, avgSize):
    sizeGap = 20 # in %
    correct_width = (avgSize[0] * (100-sizeGap) / 100
                     < point.width
                     < avgSize[0] * (100+sizeGap) / 100)
    
    correct_height = (avgSize[1] * (100-sizeGap) / 100
                      < point.width
                      < avgSize[1] * (100+sizeGap) / 100)
    return correct_width and correct_height


def draw_points_box(image, box):
    if isinstance(box, tuple):
        cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 0, 0), 3)


def get_point_box(points):
    if len(points) > 0:
        x_min = points[0].x
        x_max = points[0].x
        y_min = points[0].y
        y_max = points[0].y
        for point in points:
            x_min = min(x_min, point.x)
            x_max = max(x_max, point.x + point.width)
            y_min = min(y_min, point.y)
            y_max = max(y_max, point.y + point.height)

        return (x_min, y_min, x_max, y_max)

def add_margin(box, margin, image):
    h, w, _ = image.shape
    x_min, y_min, x_max, y_max = box[0], box[1], box[2], box[3]

    x_min = max(0, x_min - margin)
    y_min = max(0, y_min - margin)
    x_max = min(w - 1, x_max + margin)
    y_max = min(h - 1, y_max + margin)

    return (x_min, y_min, x_max, y_max)


def calc_area(point):
    """  return the air of a point """
    return point.width * point.height


def calc_avg_area(points):
    if len(points) > 0:
        area = 0 
        for point in points:
            area += calc_area(point)

        return area / len(points)


def calc_area_variance(points, avg_area):
    v = 0
    n = len(points)
    for point in points:
        v += calc_area(point)**2
    v = v / n-avg_area**2

    return v
        
def calc_avg_size(points):
    width_sum = 0
    height_sum = 0
    nb_point = len(points)
    for point in points:
        width_sum += point.width
        height_sum += point.height
    
    avg_width = width_sum / nb_point
    avg_height = height_sum / nb_point

    return (avg_width, avg_height)


def area_asc_sort(points):
    for i in range(1, len(points)):
        key_item = points[i]
        j = i - 1
        while j >= 0 and calc_area(points[j]) > calc_area(key_item):
            points[j + 1] = points[j]
            j -= 1
        points[j + 1] = key_item

    return points


def find_valid_points(points, image):
    h, w = image.shape
    count = 1
    best_points = []
    for point in points[1:]: # skip first point which is the entire frame
        if (is_square(point)
            and is_big_enough(point)
            and not is_too_big(point, w, h)):
            point.id = count
            best_points.append(point)
            point.draw_frame(image, 0, (200, 200, 200), 2)
        else:
            point.draw_frame(image, 0, (125, 125, 125), 1)
        count += 1

    return best_points


def remove_big_points(points, thresholded_image):
    avg_area = calc_avg_area(points)
    while calc_area_variance(points, avg_area) > 1000:
        if (abs(calc_area(points[-1]) - avg_area)
            > abs(calc_area(points[0]) - avg_area)):
            point_index = -1
        else:
            point_index = 0

        points[point_index].draw_circle(thresholded_image, (111, 111, 111), 2)
        del points[point_index]

        avg_area = calc_avg_area(points)


def display_points_id(image, points):
    for i in range(len(points)):
            points[i].id = i
            points[i].display_id(image, (55, 55, 55), 2)
# converting image into grayscale image


def get_braille_char_img(image, braille_char):
    top_left_corner = brailleReader.coord_to_int((braille_char.x, braille_char.y))
    bot_right_corner = brailleReader.coord_to_int((braille_char.x + braille_char.width,
                                                   braille_char.y + braille_char.height))
    
    braille_char_img = image[top_left_corner[1]:bot_right_corner[1],
                             top_left_corner[0]:bot_right_corner[0]]
    
    return braille_char_img


def threshold_image(image, threshold_value):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresholded_image = cv2.threshold(gray, threshold_value, 255,
                                         cv2.THRESH_BINARY)
    
    return thresholded_image


def translate_braille_chars(thresholded_image, braille_chars):
    for braille_char in braille_chars:
        braille_char_img = get_braille_char_img(thresholded_image, braille_char)
        # braille_char_img = threshold_image(image, threshold_value)
        braille_char.translation = translator.translate(braille_char_img)


def display_translations(image, braille_chars):
    for braille_char in braille_chars:
        top_left_corner = brailleReader.coord_to_int((braille_char.x, braille_char.y))
        bot_right_corner = brailleReader.coord_to_int((braille_char.x + braille_char.width,
                                                        braille_char.y + braille_char.height))
        cv2.putText(image, braille_char.translation
                    , coord_to_int((braille_char.x + braille_char.width/2
                       , bot_right_corner[1] + 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)
        cv2.rectangle(image, top_left_corner,
                        bot_right_corner, [0, 0, 255])


def display_roi(image, points, threshold_value):
    points_box = get_point_box(points)
    points_box = add_margin(points_box, 15, image)

    roi = image.copy()
    roi = roi[points_box[1]:points_box[3], points_box[0]:points_box[2]]
    cv2.imshow("ROI", roi)

    thresholded_roi = threshold_image(roi, threshold_value)
    cv2.imshow("Thresholded ROI", thresholded_roi)


def get_potential_points(thresholded_image):
    contours, _ = cv2.findContours(
        thresholded_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    return list(brailleReader.Point(contour) for contour in contours)


def get_points(image, thresholded_image):
    points = get_potential_points(thresholded_image)

    best_points = []
    if points: 
        best_points = find_valid_points(points, thresholded_image)
        
    if best_points:
        area_asc_sort(best_points)
        remove_big_points(best_points, thresholded_image)

        # display_roi(image, best_points)

        display_points_id(image, best_points)

    # cv2.imshow("Threshlolded", thresholded_image)
    print("points : ", len(best_points))
    return best_points

