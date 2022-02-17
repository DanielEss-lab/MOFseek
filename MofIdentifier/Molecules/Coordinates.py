import math

import numpy as np


def conversion_to_Cartesian(atom_a, atom_b, atom_c, angles, lengths, volume):
    alpha = angles[0] * math.pi / 180
    beta = angles[1] * math.pi / 180
    gamma = angles[2] * math.pi / 180
    sin_gamma = math.sin(gamma)
    cos_beta = math.cos(beta)
    cos_gamma = math.cos(gamma)
    value_of_trig = (math.cos(alpha) - (cos_beta * cos_gamma)) / sin_gamma

    matrix = np.array([[lengths[0], (lengths[1] * cos_gamma), (lengths[2] * cos_beta)],
                       [0, (lengths[1] * sin_gamma), lengths[2] * value_of_trig],
                       [0, 0, volume / (lengths[0] * lengths[1] * sin_gamma)]])

    return np.matmul(matrix, np.array([atom_a, atom_b, atom_c]))


def convert_to_fractional(atom_x, atom_y, atom_z, mof):
    alpha = mof.angles[0] * math.pi / 180
    beta = mof.angles[1] * math.pi / 180
    gamma = mof.angles[2] * math.pi / 180
    omega = mof.unit_volume
    sin_gamma = math.sin(gamma)
    cos_beta = math.cos(beta)
    cos_gamma = math.cos(gamma)
    cos_alpha = math.cos(alpha)
    conversion_matrix = np.array([[1 / mof.fractional_lengths[0], -cos_gamma / (mof.fractional_lengths[0] * sin_gamma),
                                   mof.fractional_lengths[1] * mof.fractional_lengths[2] * (cos_alpha * cos_gamma - cos_beta) / (omega * sin_gamma)],
                                  [0, 1 / (mof.fractional_lengths[1] * sin_gamma),
                                   mof.fractional_lengths[0] * mof.fractional_lengths[2] * (cos_beta * cos_gamma - cos_alpha) / (omega * sin_gamma)],
                                  [0, 0, mof.fractional_lengths[0] * mof.fractional_lengths[1] * sin_gamma / omega]])
    return np.matmul(conversion_matrix, np.array([atom_x, atom_y, atom_z]))
