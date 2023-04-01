import cv2, time, numpy as np
from math import *
from .utils import *
from . import roiFinderV3
from . import brailleConstants as brCst

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
        center = coord_to_int((self.x + self.width/2, self.y + self.height/2))
        center2 = (center[0] - 2, center[1] - 2)
        cv2.putText(image, str(self.id), center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 230, 230), thickness)
        cv2.putText(image, str(self.id), center2, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)


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
    
    return (x_distance <= point1.width * brCst.X_DISTANCE_COEF
            and y_distance <= point1.height * brCst.Y_DISTANCE_COEF)


def find_point(point_group, points, debug_image, debug):
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
                    find_point(point_group, points, debug_image, debug)
                    if debug:
                        cv2.line(debug_image, ((int)(parent_point_center[0]),
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
    default_w = brCst.XP * mean(points_w)
    default_h = brCst.YP * mean(points_h)

    return default_w, default_h


def resize_braille_chars(braille_chars, best_w, best_h, image, debug):
    for braille_char in braille_chars:
        default_w, default_h = default_size(braille_char)
        if debug:
            tlc = (braille_char.x, braille_char.y)
            brc = (tlc[0] + braille_char.width, tlc[1] + braille_char.height)

            # if (braille_char.height >= default_h
            #     and braille_char.width >= default_w):
            #     cv2.rectangle(image, coord_to_int(tlc),
            #                     coord_to_int(brc), (0, 0, 0), 2)
            # else:
            cv2.rectangle(image, coord_to_int(tlc),
                            coord_to_int(brc), (0, 0, 0), 1)

        if braille_char.width < default_w:
            braille_char.width = best_w if best_w != 0 else default_w
        if braille_char.height < default_h:
            braille_char.height = best_h if best_h != 0 else default_h
        # tlc = (braille_char.x, braille_char.y)
        # brc = (tlc[0] + braille_char.width, tlc[1] + braille_char.height)

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


def find_point_groups(points, debug_img, debug):
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

            find_point(point_group, points, debug_img, debug)
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
        best_width = int(brCst.XP * mean(points_w))
    if len(boxes_h) > 0:
        best_height = int(mean(boxes_h))
    else:
        best_height = int(brCst.YP * mean(points_h))
    
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


def get_braille_chars(input_img, debug_img, debug):
    points = roiFinderV3.get_points(debug_img, debug)
    
    if debug:
        roiFinderV3.display_points_id(input_img, points)
        
    point_groups = find_point_groups(points, debug_img, debug)
    
    braille_chars = create_braille_chars(point_groups, debug_img)
    best_w, best_h = get_best_sizes(braille_chars, debug_img)
    resize_braille_chars(braille_chars, best_w, best_h, debug_img, debug)
    braille_chars = remove_overlapping_boxes(braille_chars, debug_img)
    
    return braille_chars


def get_points_nb(input_img, threshold_value):
    thresholded_image = roiFinderV3.threshold_image(input_img,
                                                    threshold_value)
    points = roiFinderV3.get_points(thresholded_image,
                                    False)
    
    return len(points)


def comp_threshold_interval(pts_lens, l_val, u_val, step_val):
    if (pts_lens[0] >= pts_lens[1] and pts_lens[0] > pts_lens[2]):
        u_val -= step_val
    elif (pts_lens[2] >= pts_lens[1] and pts_lens[2] > pts_lens[0]):
        l_val += step_val
    elif (pts_lens[1] > pts_lens[0] and pts_lens[1] > pts_lens[2]):
        u_val -= int(0.5 * step_val)
        l_val += int(0.5 * step_val)
    else:
        print("error", pts_lens)
    return l_val, u_val

def find_best_threshold(input_img, spilt_nb=3):
    lower_value ,upper_value = 0, 255

    itera = 1
    points_lens = [0, 1, 1, 2]
    while not (points_lens[0] == points_lens[1] == points_lens[2]):
        print("iteration : ", itera, lower_value, upper_value)
        step_value = int((upper_value-lower_value) / (spilt_nb+1))
        new_points_lens = []
        for i in range(spilt_nb):
            threshold_value = lower_value + (i+1)*step_value
            new_points_lens.append(get_points_nb(input_img.copy(),
                                             threshold_value))

        if new_points_lens != points_lens:
            points_lens = new_points_lens.copy()
        else:
            print("Same number of points")
            break
        print(points_lens)
        itera += 1
        lower_value, upper_value = comp_threshold_interval(
            points_lens, lower_value, upper_value, step_value)
    threshold_value -= step_value

    return threshold_value


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