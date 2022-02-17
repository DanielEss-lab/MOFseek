import numpy as np


def conversion_to_Cartesian(atom_a, atom_b, atom_c, angles, lengths, volume):
    alpha = np.deg2rad(angles[0])
    beta = np.deg2rad(angles[1])
    gamma = np.deg2rad(angles[2])
    length_a = lengths[0]
    length_b = lengths[1]
    length_c = lengths[2]

    value_of_trig = (np.cos(alpha) - (np.cos(beta) * np.cos(gamma))) / np.sin(gamma)

    matrix = np.array([[length_a, (length_b * np.cos(gamma)), (length_c * np.cos(beta))],
                       [0, (length_b * np.sin(gamma)), length_c * value_of_trig],
                       [0, 0, volume / (length_a * length_b * np.sin(gamma))]])

    return np.matmul(matrix, np.array([atom_a, atom_b, atom_c]))


def convert_to_fractional(atom_x, atom_y, atom_z, mof):
    alpha = np.deg2rad(mof.angles[0])
    beta = np.deg2rad(mof.angles[1])
    gamma = np.deg2rad(mof.angles[2])
    a = mof.fractional_lengths[0]
    b = mof.fractional_lengths[1]
    c = mof.fractional_lengths[2]
    omega = mof.unit_volume
    conversion_matrix = np.array([[1 / a, -np.cos(gamma) / (a * np.sin(gamma)),
                                   b * c * (np.cos(alpha) * np.cos(gamma) - np.cos(beta)) / (omega * np.sin(gamma))],
                                  [0, 1 / (b * np.sin(gamma)),
                                   a * c * (np.cos(beta) * np.cos(gamma) - np.cos(alpha)) / (omega * np.sin(gamma))],
                                  [0, 0, a * b * np.sin(gamma) / omega]])
    return np.matmul(conversion_matrix, np.array([atom_x, atom_y, atom_z]))