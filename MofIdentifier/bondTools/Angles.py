import numpy as np

from MofIdentifier.bondTools import Distances


def angle(end_a, middle, end_b, angles, lengths):
    dist_a = Distances.distance_across_unit_cells(end_a, middle, angles, lengths)
    dist_b = Distances.distance_across_unit_cells(end_b, middle, angles, lengths)
    dist_c = Distances.distance_across_unit_cells(end_a, end_b, angles, lengths)
    if dist_a < 0.005 or dist_b < 0.005:
        return float('NaN')
    arccos_input = (dist_a ** 2 + dist_b ** 2 - dist_c ** 2) / (2 * dist_a * dist_b)
    if arccos_input > 1 or arccos_input < -1:
        return float('NaN')
    c_angle = np.arccos(arccos_input)
    return c_angle


def degrees(radians):
    return radians / np.pi * 180
