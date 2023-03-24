import cv2
from math import *
import translator
import brailleReaderV6debug  as brailleReader
from src.utils import *


def is_square(point):
    gap = 20 # in %

    return (point.height * 100 / (100+gap)
            < point.width
            < point.height * 100 / (100-gap))


def is_big_enough(point):
    min_lenght = 7
    return point.width > min_lenght and point.height > min_lenght


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
    count = 1
    best_points = []
    for point in points[1:]: # skip first point which is the entire frame
        if is_square(point) and is_big_enough(point):
            point.id = count
            best_points.append(point)
            point.draw_frame(image, 0, (200, 200, 200), 2)
        else:
            point.draw_frame(image, 0, (125, 125, 125), 1)
        count += 1

    return best_points


def remove_big_points(points):
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


cap = cv2.VideoCapture(0)
image0 = cv2.imread('./res/videoImage.png')

# converting image into grayscale image
gray0 = cv2.cvtColor(image0, cv2.COLOR_BGR2GRAY)

size_threshold = 120
mythreshold_id = 115

while True:
    ret, image = cap.read()
    # image = cv2.imread('./res/videoImage.png')
    if not ret:
        continue
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #gray = gray0.copy()
    #image = image0.copy()
    
    _, thresholded_image = cv2.threshold(gray, mythreshold_id, 255,
                                         cv2.THRESH_BINARY)

    # using a findContours() functioncircle
    contours, _ = cv2.findContours(
        thresholded_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    points = list(brailleReader.Point(contour) for contour in contours)
    best_points = []

    if len(points) > 1: 
        best_points = find_valid_points(points, thresholded_image)

    area_asc_sort(best_points)

    if len(best_points) > 1:
        remove_big_points(best_points)

        points_box = get_point_box(best_points)
        # print("->", points_box, image.shape, (points_box[2] - points_box[0], points_box[3] - points_box[1]))
        points_box = add_margin(points_box, 15, image)

        roi = image.copy()
        roi = roi[points_box[1]:points_box[3], points_box[0]:points_box[2]]
        # print(points_box, image.shape, (points_box[2] - points_box[0], points_box[3] - points_box[1]))
        cv2.imshow("ROI", roi) 
        
        braille_chars = brailleReader.translate(image, best_points)
        for braille_char in braille_chars:
            brailleReader.display_boxes(image, braille_chars)


        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # setting threshold of gray image
        _, threshold = cv2.threshold(gray, mythreshold_id, 255, cv2.THRESH_BINARY)
        
        cv2.imshow("Thresholded ROI", threshold)

        for i in range(len(braille_chars)):
            top_left_corner2 = coordToInt((braille_chars[i].x, braille_chars[i].y))
            bot_right_corner2 = (top_left_corner2[0] + int(braille_chars[i].width),
                         top_left_corner2[1] + int(braille_chars[i].height))
            
            top_left_corner = (top_left_corner2[0] - points_box[0]
                               , top_left_corner2[1] - points_box[1])
            bot_right_corner = (top_left_corner[0] + int(braille_chars[i].width),
                        top_left_corner[1] + int(braille_chars[i].height))
            
            braille_char = threshold[top_left_corner[1]:bot_right_corner[1],
                                     top_left_corner[0]:bot_right_corner[0]]

            traslation = translator.translate(braille_char)
            cv2.putText(image, traslation, bot_right_corner2, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
            cv2.rectangle(image, top_left_corner2, bot_right_corner2, [0, 0, 255])


        cv2.imshow("Result", image)

        # draw_points_box(image, points_box)
        display_points_id(image, best_points)
            # print(i, " : ", calc_area(best_points[i]), avg_area)
    
    cv2.imshow("Image", image)
    cv2.imshow("Threshlolded", thresholded_image)

    key = cv2.waitKey(100)
    if key == ord('q'):
        break
    elif key == ord('t'):
        if mythreshold_id > 0:
            mythreshold_id -= 1
    elif key == ord('y'):
        mythreshold_id += 1
    elif key == ord('g'):
        if size_threshold > 0:
            size_threshold -= 1
    elif key == ord('h'):
        size_threshold += 1
    if key != -1:
        print("Size Threshold (g/h): ", size_threshold)
        print("Threshold (t/y) : ", mythreshold_id)
