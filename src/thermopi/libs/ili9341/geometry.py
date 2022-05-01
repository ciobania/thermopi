#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'

# A Python3 program to check if a given point
# lies inside a given polygon
# Refer to following links:
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
# https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/
# for explanations

# Define Infinite (Using INT_MAX caused overflow problems)
INT_MAX = 10000


# Given three collinear points p, q, r,
# the function checks if point q lies on the line segment 'pr'
def on_segment(p: tuple, q: tuple, r: tuple) -> bool:
    if ((q[0] <= max(p[0], r[0])) &
            (q[0] >= min(p[0], r[0])) &
            (q[1] <= max(p[1], r[1])) &
            (q[1] >= min(p[1], r[1]))):
        return True

    return False


# To find orientation of ordered triplet (p, q, r).
# The function returns following values
# 0 --> p, q and r are collinear
# 1 --> Clockwise
# 2 --> Counterclockwise
def orientation(p: tuple, q: tuple, r: tuple) -> int:
    val = (((q[1] - p[1]) *
            (r[0] - q[0])) -
           ((q[0] - p[0]) *
            (r[1] - q[1])))

    if val == 0:
        return 0
    if val > 0:
        return 1  # Collinear
    else:
        return 2  # Clock or counter-clock


def do_intersect(p1, q1, p2, q2):
    # Find the four orientations needed for general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases
    # p1, q1 and p2 are collinear and
    # p2 lies on segment p1q1
    if (o1 == 0) and (on_segment(p1, p2, q1)):
        return True

    # p1, q1 and p2 are collinear and
    # q2 lies on segment p1q1
    if (o2 == 0) and (on_segment(p1, q2, q1)):
        return True

    # p2, q2 and p1 are collinear and
    # p1 lies on segment p2q2
    if (o3 == 0) and (on_segment(p2, p1, q2)):
        return True

    # p2, q2 and q1 are collinear and
    # q1 lies on segment p2q2
    if (o4 == 0) and (on_segment(p2, q1, q2)):
        return True

    return False


# Returns true if the point p lies
# inside the polygon[] with n vertices
def is_inside_polygon(points, position):
    n = len(points)

    # There must be at least 3 vertices
    # in polygon
    if n < 3:
        return False

    # Create a point for line segment
    # from p to infinite
    extreme = (INT_MAX, position[1])
    count = i = 0

    while True:
        next_element = (i + 1) % n

        # Check if the line segment from 'p' to
        # 'extreme' intersects with the line
        # segment from 'polygon[i]' to 'polygon[next]'
        if (do_intersect(points[i],
                         points[next_element],
                         position, extreme)):

            # If the point 'p' is collinear with line
            # segment 'i-next', then check if it lies
            # on segment. If it lies, return true, otherwise false
            if orientation(points[i], position,
                           points[next_element]) == 0:
                return on_segment(points[i], position,
                                  points[next_element])

            count += 1
        i = next_element
        if i == 0:
            break

    # Return true if count is odd, false otherwise
    return count % 2 == 1


# Driver code
if __name__ == '__main__':
    # polygon1 = [(0, 0), (10, 0), (10, 10), (0, 10)]
    polygon1 = [[140.375, 270.078125], [102, 270.078125], [102, 228.5703125], [140.375, 228.5703125]]

    random_point = (20, 20)
    if is_inside_polygon(points=polygon1, position=random_point):
        print('Yes')
    else:
        print('No')

    # random_point = (5, 5)
    random_point = (110, 230)
    # random_point = [[179.46875, 270.078125], [157.15625, 270.078125], [158.703125, 214.0], [193.853515625, 210.8828125]]
    if is_inside_polygon(points=polygon1, position=random_point):
        print('Yes')
    else:
        print('No')

    polygon2 = [(0, 0), (5, 0), (5, 5), (3, 3)]
    random_point = (3, 3)
    if is_inside_polygon(points=polygon2, position=random_point):
        print('Yes')
    else:
        print('No')

    random_point = (5, 1)
    if is_inside_polygon(points=polygon2, position=random_point):
        print('Yes')
    else:
        print('No')

    random_point = (8, 1)
    if is_inside_polygon(points=polygon2, position=random_point):
        print('Yes')
    else:
        print('No')

    polygon3 = [(0, 0), (10, 0), (10, 10), (0, 10)]
    random_point = (-1, 10)
    if is_inside_polygon(points=polygon3, position=random_point):
        print('Yes')
    else:
        print('No')

# This code is contributed by Vikas Chitturi
