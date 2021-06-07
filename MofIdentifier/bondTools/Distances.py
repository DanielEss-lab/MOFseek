import math

from MofIdentifier.bondTools.CovalentRadiusLookup import lookup

bond_length_flat_error_margin = 0.05
bond_length_multiplicative_error_margin = 1.10


def distance(a, b):
    ax, ay, az = a.x, a.y, a.z
    bx, by, bz = b.x, b.y, b.z
    return math.sqrt((bx - ax) ** 2 + (by - ay) ** 2 + (bz - az) ** 2)


def is_bond_distance(d, a, b):
    rad_a = lookup(a.type_symbol)
    rad_b = lookup(b.type_symbol)
    return d < (rad_a + rad_b) * bond_length_multiplicative_error_margin + bond_length_flat_error_margin


def are_within_bond_range(a, b):
    return is_bond_distance(distance(a, b), a, b)
