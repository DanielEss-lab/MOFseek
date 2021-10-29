import math

from MofIdentifier.bondTools.CovalentRadiusLookup import lookup

bond_length_flat_error_margin = 0.05
bond_length_multiplicative_error_margin = 1.10
metal_bond_breakup_angle_margin = 0.88  # About a 45 degree angle


def distance(a, b):
    ax, ay, az = a.x, a.y, a.z
    bx, by, bz = b.x, b.y, b.z
    return math.sqrt((bx - ax) ** 2 + (by - ay) ** 2 + (bz - az) ** 2)


def distance_across_unit_cells(base_atom, neighbor, angles, lengths):
    possible_neighbor_locations = [move_neighbor_if_distant(base_atom, neighbor, angles, lengths, 0.40),
                                   # move_neighbor_if_distant(base_atom, neighbor, angles, lengths, 0.45),
                                   # move_neighbor_if_distant(base_atom, neighbor, angles, lengths, 0.50),
                                   # move_neighbor_if_distant(base_atom, neighbor, angles, lengths, 0.55),
                                   move_neighbor_if_distant(base_atom, neighbor, angles, lengths, 0.60)]
    distances = (distance(base_atom, neighbor_copy) for neighbor_copy in possible_neighbor_locations)
    return min(distances)


def move_neighbor_if_distant(base_atom, neighbor, angles, lengths, fractional_distance_required=0.48):
    da = db = dc = 0
    if neighbor.a - base_atom.a > fractional_distance_required:
        da -= 1.0
    elif neighbor.a - base_atom.a < -fractional_distance_required:
        da += 1.0
    if neighbor.b - base_atom.b > fractional_distance_required:
        db -= 1.0
    elif neighbor.b - base_atom.b < -fractional_distance_required:
        db += 1.0
    if neighbor.c - base_atom.c > fractional_distance_required:
        dc -= 1.0
    elif neighbor.c - base_atom.c < -fractional_distance_required:
        dc += 1.0

    # The next (lengthy) section will try to change each dimension greedily to see if there's a better adj solution
    new_da, new_db, new_dc = da, db, dc
    best_dist = distance(base_atom, neighbor.copy_to_relative_position(da, db, dc, angles, lengths))

    while True:
        variation_dist = distance(base_atom, neighbor.copy_to_relative_position(da + 1, db, dc, angles, lengths))
        if variation_dist < best_dist - 0.001:
            new_da, new_db, new_dc = da + 1, db, dc
            best_dist = variation_dist
        variation_dist = distance(base_atom, neighbor.copy_to_relative_position(da - 1, db, dc, angles, lengths))
        if variation_dist < best_dist - 0.001:
            new_da, new_db, new_dc = da - 1, db, dc
            best_dist = variation_dist

        variation_dist = distance(base_atom, neighbor.copy_to_relative_position(da, db + 1, dc, angles, lengths))
        if variation_dist < best_dist - 0.001:
            new_da, new_db, new_dc = da, db + 1, dc
            best_dist = variation_dist
        variation_dist = distance(base_atom, neighbor.copy_to_relative_position(da, db - 1, dc, angles, lengths))
        if variation_dist < best_dist - 0.001:
            new_da, new_db, new_dc = da, db - 1, dc
            best_dist = variation_dist

        variation_dist = distance(base_atom, neighbor.copy_to_relative_position(da, db, dc + 1, angles, lengths))
        if variation_dist < best_dist - 0.001:
            new_da, new_db, new_dc = da, db, dc + 1
            best_dist = variation_dist
        variation_dist = distance(base_atom, neighbor.copy_to_relative_position(da, db, dc - 1, angles, lengths))
        if variation_dist < best_dist - 0.001:
            new_da, new_db, new_dc = da, db, dc - 1
            best_dist = variation_dist

        if (new_da, new_db, new_dc) == (da, db, dc):  # No variant was better than the start
            break
        else:
            (da, db, dc) = (new_da, new_db, new_dc)  # Set start parameters so that now it's varying the new best

    return neighbor.copy_to_relative_position(new_da, new_db, new_dc, angles, lengths)


def is_bond_distance(d, a, b, error_margin=bond_length_multiplicative_error_margin):
    rad_a = lookup(a.type_symbol)
    rad_b = lookup(b.type_symbol)
    return d < (rad_a + rad_b) * error_margin + bond_length_flat_error_margin


def are_within_bond_range(a, b):
    """Not recommended, except for specific situations, because it interacts strangely with unit cell boundaries."""
    return is_bond_distance(distance(a, b), a, b)
