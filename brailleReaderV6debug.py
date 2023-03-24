import cv2
import translator
from math import *

LOSS = 0.8
XP = 3 * LOSS
YP = 5 * LOSS

class Point:
    def __init__(self, contour):
        (self.x, self.y, self.width, self.height) = cv2.boundingRect(contour)
        self.haveAGroup = False
        self.id = None
    

    def draw_frame(self, image, margin, color = (0, 0, 0), thickness = 1):
        tlCorner = (self.x - margin, self.y - margin)
        brCorner = (self.x + self.width + margin, self.y + self.height + margin)
        cv2.rectangle(image, coordToInt(tlCorner), coordToInt(brCorner), color, thickness)


    def draw_circle(self, image, color = (0, 0, 0), thickness = 1):
        center = (self.x + self.width / 2, self.y + self.height / 2)
        cv2.circle(image, coordToInt(center), int((self.width + self.height) / 4), color, thickness)


    def displayId(self, image, color = (0, 0, 0), thickness = 1):
        center = (self.x + self.width / 2, self.y + self.height / 2)
        cv2.putText(image, str(self.id), coordToInt(center), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)


class BrailleChar:
    def __init__(self, id, points, x, y, width, height):
        self.id = id
        self.points = points
        self.x = x
        self.y = y
        self.width = width
        self.height = height


def areCloseEnough(point1, point2):
    xCoef = 2
    yCoef = 2
    xDistance = abs(point1.x - point2.x)
    yDistance = abs(point1.y - point2.y)
    return (xDistance <= point1.width * xCoef and yDistance <= point1.height * yCoef)


def coordToInt(coord):
    return(int(coord[0]), int(coord[1]))


def findPoint(pointGroup, points, image):
    parentPoint = pointGroup[-1]
    parentPointCenter = (parentPoint.x + parentPoint.width / 2,
                         parentPoint.y + parentPoint.height / 2)
    for point in points:
        if not point.haveAGroup:
            pointCenter = (point.x + point.width / 2, point.y + point.height / 2)
            if areCloseEnough(parentPoint, point):
                point.haveAGroup = True
                pointGroup.append(point)
                if len(pointGroup) < 5 :
                    findPoint(pointGroup, points, image)
                    cv2.line(image, ((int)(parentPointCenter[0]),
                                     (int)(parentPointCenter[1])),
                                    ((int)(pointCenter[0]),
                                     (int)(pointCenter[1])),
                                     (0, 0, 0), 1)


def points_shape(points):
    points_height = [point.height for point in points]
    points_width = [point.width for point in points]

    return points_height, points_width
                

def findPointBox(pointGroup, image):
    xmin = pointGroup[0].x
    ymin = pointGroup[0].y
    xmax = xmin
    ymax = ymin

    for point in pointGroup:
        ymax = max(ymax, point.y + point.height)
        ymin = min(ymin, point.y)
        xmax = max(xmax, point.x + point.width)
        xmin = min(xmin, point.x)
    
    cv2.rectangle(image, coordToInt((xmin, ymin)), coordToInt((xmax, ymax)), (0, 0, 0), 2)
    return(xmin, ymin, xmax - xmin, ymax - ymin)


def default_size(braille_char):
    points_w, points_h = points_shape(braille_char.points)
    default_w = XP * mean(points_w)
    default_h = YP * mean(points_h)

    return default_w, default_h


def resize_braille_chars(braille_chars, best_w, best_h, image):
    for braille_char in braille_chars:
        default_w, default_h = default_size(braille_char)

        if braille_char.height < default_h:
            tlc = (braille_char.x, braille_char.y)
            brc = (tlc[0] + braille_char.width, tlc[1] + braille_char.height)
            cv2.rectangle(image, coordToInt(tlc), coordToInt(brc), (0, 0, 0), 2)

        if braille_char.width < default_w:
            braille_char.width = best_w if best_w != 0 else default_w
        if braille_char.height < default_h:
            braille_char.height = best_h if best_h != 0 else default_h 
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
        x, y, width, height = findPointBox(point_groups[i], image)
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
    pointGroups = []
    allPointsHaveGroup = False
    while not allPointsHaveGroup:
        pointIndex = 0
        while pointIndex < len(points) and points[pointIndex].haveAGroup:
            pointIndex += 1
        if pointIndex < len(points) and not points[pointIndex].haveAGroup:
            mainPoint = points[pointIndex]  # point sans groupe
            points[pointIndex].haveAGroup = True # indique que ce point d'est plus disponible (on va lui trouver son groupe)
            pointGroup = [mainPoint]

            findPoint(pointGroup, points, image)
            pointGroups.append(pointGroup)
        else:
            allPointsHaveGroup = True

    return pointGroups


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
    xDistance = abs(braille_char_1.x - braille_char_2.x)
    yDistance = abs(braille_char_1.y - braille_char_2.y)
    
    mean_w = mean((braille_char_1.width, braille_char_2.width))
    mean_h = mean((braille_char_1.height, braille_char_2.height))

    return (xDistance < mean_w and yDistance < mean_h)


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
        cv2.rectangle(image, coordToInt(tlc), coordToInt(brc), (5, 5, 5), 2)


def translate(image, points):

    pointGroups = find_point_groups(points, image)
    
    braille_chars = create_braille_chars(pointGroups, image)
    best_w, best_h = get_best_sizes(braille_chars, image)
    resize_braille_chars(braille_chars, best_w, best_h, image)

    # display_boxes(image, braille_chars)
    new_braille_chars = remove_overlapping_boxes(braille_chars, image)

    return new_braille_chars