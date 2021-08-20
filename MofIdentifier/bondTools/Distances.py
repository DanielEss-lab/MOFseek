import math

from MofIdentifier.bondTools.CovalentRadiusLookup import lookup

bond_length_flat_error_margin = 0.05
bond_length_multiplicative_error_margin = 1.10


def distance(a, b):
    ax, ay, az = a.x, a.y, a.z
    bx, by, bz = b.x, b.y, b.z
    return math.sqrt((bx - ax) ** 2 + (by - ay) ** 2 + (bz - az) ** 2)


def distance_across_unit_cells(base_atom, neighbor, angles, lengths):
    da = db = dc = 0
    if neighbor.a - base_atom.a > 0.5:
        da -= 1.0
    elif neighbor.a - base_atom.a < -0.5:
        da += 1.0
    if neighbor.b - base_atom.b > 0.5:
        db -= 1.0
    elif neighbor.b - base_atom.b < -0.5:
        db += 1.0
    if neighbor.c - base_atom.c > 0.5:
        dc -= 1.0
    elif neighbor.c - base_atom.c < -0.5:
        dc += 1.0
    neighbor_in_right_place = neighbor.copy_to_relative_position(da, db, dc, angles,lengths)
    return distance(base_atom, neighbor_in_right_place)


def is_bond_distance(d, a, b, error_margin=bond_length_multiplicative_error_margin):
    rad_a = lookup(a.type_symbol)
    rad_b = lookup(b.type_symbol)
    return d < (rad_a + rad_b) * error_margin + bond_length_flat_error_margin


def are_within_bond_range(a, b):
    """Not recommended, except for specific situations, because it interacts strangely with unit cell boundaries."""
    return is_bond_distance(distance(a, b), a, b)
