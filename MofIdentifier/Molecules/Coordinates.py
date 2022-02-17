import math

import numpy as np


def conversion_to_Cartesian(atom_a, atom_b, atom_c, angles, lengths, volume):
    alpha = angles[0] * math.pi / 180
    beta = angles[1] * math.pi / 180
    gamma = angles[2] * math.pi / 180
    length_a = lengths[0]
    length_b = lengths[1]
    length_c = lengths[2]

    value_of_trig = (math.cos(alpha) - (math.cos(beta) * math.cos(gamma))) / math.sin(gamma)

    matrix = np.array([[length_a, (length_b * math.cos(gamma)), (length_c * math.cos(beta))],
                       [0, (length_b * math.sin(gamma)), length_c * value_of_trig],
                       [0, 0, volume / (length_a * length_b * math.sin(gamma))]])

    return np.matmul(matrix, np.array([atom_a, atom_b, atom_c]))


def convert_to_fractional(atom_x, atom_y, atom_z, mof):
    alpha = mof.angles[0] * math.pi / 180
    beta = mof.angles[1] * math.pi / 180
    gamma = mof.angles[2] * math.pi / 180
    a = mof.fractional_lengths[0]
    b = mof.fractional_lengths[1]
    c = mof.fractional_lengths[2]
    omega = mof.unit_volume
    conversion_matrix = np.array([[1 / a, -math.cos(gamma) / (a * math.sin(gamma)),
                                   b * c * (math.cos(alpha) * math.cos(gamma) - math.cos(beta)) / (omega * math.sin(gamma))],
                                  [0, 1 / (b * math.sin(gamma)),
                                   a * c * (math.cos(beta) * math.cos(gamma) - math.cos(alpha)) / (omega * math.sin(gamma))],
                                  [0, 0, a * b * math.sin(gamma) / omega]])
    return np.matmul(conversion_matrix, np.array([atom_x, atom_y, atom_z]))
