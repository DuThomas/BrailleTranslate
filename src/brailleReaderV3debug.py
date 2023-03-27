import cv2
from math import *
from .utils import *
from . import roiFinderV3debug

LOSS = 0.8
XP = 3 * LOSS
YP = 5 * LOSS

X_DISTANCE_COEF = 2
Y_DISTANCE_COEF = 2

class Point:
    def __init__(self, contour):
        (self.x, self.y, self.width, self.height) = cv2.boundingRect(contour)
        self.have_group = False
        self.id = None
    

    def draw_frame(self, image, margin, color=(0, 0, 0), thickness=1):
        top_left_corner = coord_to_int((self.x - margin, self.y - margin))
        bot_right_corner = coord_to_int((self.x + self.width + margin, self.y + self.height + margin))
        cv2.rectangle(image, top_left_corner, bot_right_corner, color, thickness)


    def draw_circle(self, image, color=(0, 0, 0), thickness=1):
        center = (self.x + self.width/2, self.y + self.height/2)
        cv2.circle(image, coord_to_int(center), int((self.width+self.height) / 4), color, thickness)


    def display_id(self, image, color = (0, 0, 0), thickness = 1):
        center = (self.x + self.width/2, self.y + self.height/2)
        cv2.putText(image, str(self.id), coord_to_int(center), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)


class BrailleChar:
    def __init__(self, id, points, x, y, width, height):
        self.id = id
        self.points = points
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.translation = ""


def are_close_enough(point1, point2):
    x_distance = abs(point1.x - point2.x)
    y_distance = abs(point1.y - point2.y)
    return (x_distance <= point1.width * X_DISTANCE_COEF
            and y_distance <= point1.height * Y_DISTANCE_COEF)


def findPoint(point_group, points, image):
    parent_point = point_group[-1]
    parent_point_center = (parent_point.x + parent_point.width/2,
                         parent_point.y + parent_point.height/2)
    for point in points:
        if not point.have_group:
            point_center = (point.x + point.width/2, point.y + point.height/2)
            if are_close_enough(parent_point, point):
                point.have_group = True
                point_group.append(point)
                if len(point_group) < 5 :
                    findPoint(point_group, points, image)
                    cv2.line(image, ((int)(parent_point_center[0]),
                                     (int)(parent_point_center[1])),
                                    ((int)(point_center[0]),
                                     (int)(point_center[1])),
                                     (0, 0, 0), 1)


def points_shape(points):
    points_height = [point.height for point in points]
    points_width = [point.width for point in points]

    return points_height, points_width
                

def find_point_box(point_group, image):
    x_min = point_group[0].x
    y_min = point_group[0].y
    x_max = x_min
    y_max = y_min

    for point in point_group:
        y_max = max(y_max, point.y + point.height)
        y_min = min(y_min, point.y)
        x_max = max(x_max, point.x + point.width)
        x_min = min(x_min, point.x)
    
    # cv2.rectangle(image, coord_to_int((x_min, y_min)),
    #               coord_to_int((x_max, y_max)), (0, 0, 0), 2)

    return(x_min, y_min, x_max - x_min, y_max - y_min)


def default_size(braille_char):
    points_w, points_h = points_shape(braille_char.points)
    default_w = XP * mean(points_w)
    default_h = YP * mean(points_h)

    return default_w, default_h


def resize_braille_chars(braille_chars, best_w, best_h, image):
    for braille_char in braille_chars:
        default_w, default_h = default_size(braille_char)

        # tlc = (braille_char.x, braille_char.y)
        # brc = (tlc[0] + braille_char.width, tlc[1] + braille_char.height)

        # if (braille_char.height >= default_h
        #     and braille_char.width >= default_w):
        #     cv2.rectangle(image, coord_to_int(tlc),
        #                     coord_to_int(brc), (0, 0, 0), 2)
        # else:
        #     cv2.rectangle(image, coord_to_int(tlc),
        #                     coord_to_int(brc), (0, 0, 0), 1)

        if braille_char.width < default_w:
            braille_char.width = best_w if best_w != 0 else default_w
        if braille_char.height < default_h:
            braille_char.height = best_h if best_h != 0 else default_h
        tlc = (braille_char.x, braille_char.y)
        brc = (tlc[0] + braille_char.width, tlc[1] + braille_char.height)

        # cv2.rectangle(image, coord_to_int(tlc),
        #                 coord_to_int(brc), (0, 0, 0), 1)
    # character box =! points box (character box >= points box)


def get_best_sizes(braille_chars, image):
    good_widths = []
    good_heights = []
    for braille_char in braille_chars:
        default_w, default_h = default_size(braille_char)

        if braille_char.width >= default_w:
            good_widths.append(braille_char.width)
        if braille_char.height >= default_h:
            good_heights.append(braille_char.height)

    best_w = mean(good_widths) if len(good_widths) > 0 else 0
    best_h = mean(good_heights) if len(good_heights) > 0 else 0
    
    return best_w, best_h


def create_braille_chars(point_groups, image):
    braille_chars = []
    for i in range(len(point_groups)):
        x, y, width, height = find_point_box(point_groups[i], image)
        braille_char = BrailleChar(i, point_groups[i], x, y, width, height)
        braille_chars.append(braille_char)
    return braille_chars


def zoom(image, zoom):
    width = int(image.shape[1] * zoom / 100)
    height = int(image.shape[0] * zoom / 100)
    dim = (width, height)
    image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    return image


def find_point_groups(points, image):
    point_groups = []
    all_points_have_group = False
    while not all_points_have_group:
        point_index = 0
        while point_index < len(points) and points[point_index].have_group:
            point_index += 1
        if point_index < len(points) and not points[point_index].have_group:
            mainPoint = points[point_index]  # point sans groupe
            points[point_index].have_group = True # indique que ce point d'est plus disponible (on va lui trouver son groupe)
            point_group = [mainPoint]

            findPoint(point_group, points, image)
            point_groups.append(point_group)
        else:
            all_points_have_group = True

    return point_groups


def mean(values):
    sum = 0
    for value in values:
        sum += value

    return sum / len(values)


def find_best_box_size(boxes_w, boxes_h, points_w, points_h):
    if len(boxes_w) > 0:
        best_width = int(mean(boxes_w))
    else : 
        best_width = int(XP * mean(points_w))
    if len(boxes_h) > 0:
        best_height = int(mean(boxes_h))
    else:
        best_height = int(YP * mean(points_h))
    
    return best_width, best_height


def y_asc_sort(braille_chars):
    for i in range(len(braille_chars)): # trie a bulle en fonction de la position y des rectangles
        for j in range(len(braille_chars) - 1):
            if(braille_chars[j].y > braille_chars[j + 1].y):
                temp_braille_char = braille_chars[j]
                braille_chars[j] = braille_chars[j + 1]
                braille_chars[j + 1] = temp_braille_char

def intersect(braille_char_1, braille_char_2):
    x_distance = abs(braille_char_1.x - braille_char_2.x)
    y_distance = abs(braille_char_1.y - braille_char_2.y)
    
    mean_w = mean((braille_char_1.width, braille_char_2.width))
    mean_h = mean((braille_char_1.height, braille_char_2.height))

    return (x_distance < mean_w and y_distance < mean_h)


def remove_overlapping_boxes(braille_chars, image):
    
    y_asc_sort(braille_chars)
    new_braille_chars = braille_chars.copy()
    # for i in range(len(braille_chars)):
        # cv2.putText(image, str(new_braille_chars[i].id), (new_braille_chars[i].x, new_braille_chars[i].y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)
    #     print(braille_chars[i].y, end=' ')
    # print()
    for i in range(len(braille_chars)):
        # if i<len(new_braille_chars):
        #     print(new_braille_chars[i].id)
        for j in range(len(braille_chars)):
            if(i == j):
                continue    
            if intersect(braille_chars[i], braille_chars[j]):
                # print(braille_chars[i].id, "intersects", braille_chars[j].id)
                if braille_chars[j] in new_braille_chars:
                    new_braille_chars.remove(braille_chars[j])
                braille_chars[j].x = -braille_chars[j].width
                braille_chars[j].y = -braille_chars[j].height
    # print("--------------------")

    return new_braille_chars


def display_boxes(image, braille_chars):
    for braille_char in braille_chars:
        tlc = (braille_char.x, braille_char.y)
        brc = (tlc[0] + braille_char.width, tlc[1] + braille_char.height)
        cv2.rectangle(image, coord_to_int(tlc),
                      coord_to_int(brc), (0, 0, 0), 1)


def get_braille_chars(image, result, thresholded_image):
    points = roiFinderV3debug.get_points(
                                        image,
                                        thresholded_image)
    point_groups = find_point_groups(points, result)
    
    braille_chars = create_braille_chars(point_groups, result)
    best_w, best_h = get_best_sizes(braille_chars, result)
    resize_braille_chars(braille_chars, best_w, best_h, result)

    # display_boxes(result, braille_chars)
    braille_chars = remove_overlapping_boxes(braille_chars, result)
    display_boxes(result, braille_chars)
    roiFinderV3debug.translate_braille_chars(thresholded_image, braille_chars)

    return braille_chars