import numpy as np

from MofIdentifier.bondTools import Distances

max_bond_breakup_angle = 0.88  # About a 50 degree angle
bond_breakup_angle = 2.04  # About a 120 degree angle
bond_coexistance_angle = 0.98  # will not identify open site if it would be closer than this to another atom
# bond_breakup_angle_margin of 2.09 or greater breaks test_abnormal_fractional_coordinates in SBUIdentifierTest


def mof_angle(end_a, middle, end_b, angles, lengths, volume):
    dist_a = Distances.distance_across_unit_cells(end_a, middle, angles, lengths, volume)
    dist_b = Distances.distance_across_unit_cells(end_b, middle, angles, lengths, volume)
    dist_c = Distances.distance_across_unit_cells(end_a, end_b, angles, lengths, volume)
    if dist_a < 0.005 or dist_b < 0.005:
        return float('NaN')
    arccos_input = (dist_a ** 2 + dist_b ** 2 - dist_c ** 2) / (2 * dist_a * dist_b)
    if arccos_input > 1 or arccos_input < -1:
        return float('NaN')
    c_angle = np.arccos(arccos_input)
    return c_angle


def angle(end_a, middle, end_b):
    dist_a = Distances.distance(end_a, middle)
    dist_b = Distances.distance(end_b, middle)
    dist_c = Distances.distance(end_a, end_b)
    if dist_a < 0.005 or dist_b < 0.005:
        return float('NaN')
    arccos_input = (dist_a ** 2 + dist_b ** 2 - dist_c ** 2) / (2 * dist_a * dist_b)
    if arccos_input > 1 or arccos_input < -1:
        return float('NaN')
    c_angle = np.arccos(arccos_input)
    return c_angle


def degrees(radians):
    return radians / np.pi * 180
