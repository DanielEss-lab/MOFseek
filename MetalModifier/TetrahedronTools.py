# SPDX-License-Identifier: CC0-1.0
# This file is in Public Domain.

from MetalModifier.custom_vector import Vector, sqrt


def find_fourth_vertex(vertex1, vertex2, vertex3, distance1, distance2, distance3):
    # Use Vector type for the vertices
    p1 = Vector(vertex1[0], vertex1[1], vertex1[2])
    p2 = Vector(vertex2[0], vertex2[1], vertex2[2])
    p3 = Vector(vertex3[0], vertex3[1], vertex3[2])

    # Use float type for the distances
    r1 = float(distance1)
    r2 = float(distance2)
    r3 = float(distance3)

    u_axis = (p2 - p1).unit
    v_axis = (p3 - p1).perp(u_axis).unit
    w_axis = u_axis ^ v_axis

    u2 = (p2 - p1) | u_axis
    u3 = (p3 - p1) | u_axis
    v3 = (p3 - p1) | v_axis

    u = (r1*r1 - r2*r2 + u2*u2) / (2*u2)
    v = (r1*r1 - r3*r3 + u3*u3 + v3*v3 - 2*u*u3) / (2*v3)
    w = sqrt(r1*r1 - u*u - v*v)

    return (p1 + u*u_axis + v*v_axis + w*w_axis,
            p1 + u*u_axis + v*v_axis - w*w_axis)