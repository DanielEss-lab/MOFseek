# SPDX-License-Identifier: CC0-1.0
# This file is in Public Domain.

from math import sqrt

class Vector(tuple):
    """Tuple subclass implementing basic 3D vectors"""

    def __new__(cls, x, y, z):
        return tuple.__new__(cls, (float(x), float(y), float(z)))

    def perp(self, other):
        """Part perpendicular to other vector"""
        dp = self[0]*other[0] + self[1]*other[1] + self[2]*other[2]
        return Vector(self[0] - dp*other[0],
                      self[1] - dp*other[1],
                      self[2] - dp*other[2])

    @property
    def unit(self):
        """Scaled to unit length"""
        n = sqrt(self[0]*self[0] + self[1]*self[1] + self[2]*self[2])
        return Vector(self[0]/n, self[1]/n, self[2]/n)

    @property
    def norm(self):
        """Euclidean length"""
        return sqrt(self[0]*self[0] + self[1]*self[1] + self[2]*self[2])

    @property
    def normsqr(self):
        """Euclidean length squared"""
        return self[0]*self[0] + self[1]*self[1] + self[2]*self[2]

    @property
    def x(self):
        """Vector x coordinate"""
        return self[0]

    @property
    def y(self):
        """Vector y coordinate"""
        return self[1]

    @property
    def z(self):
        """Vector z coordinate"""
        return self[2]

    def __bool__(self):
        """Nonzero vector"""
        return (self[0]*self[0] + self[1]*self[1] + self[2]*self[2] > 0)

    def __abs__(self):
        """abs(a): Euclidean length of vector a"""
        return sqrt(self[0]*self[0] + self[1]*self[1] + self[2]*self[2])

    def __add__(self, other):
        """a + b: Vector addition"""
        if isinstance(other, (tuple, list)) and len(other) >= 3:
            return Vector(self[0]+other[0], self[1]+other[1], self[2]+other[2])
        else:
            return NotImplemented

    def __radd__(self, other):
        """b + a: Vector addition"""
        if isinstance(other, (tuple, list)) and len(other) >= 3:
            return Vector(other[0]+self[0], other[1]+self[1], other[2]+self[2])
        else:
            return NotImplemented

    def __mul__(self, other):
        """a * b: Scalar multiplication"""
        if isinstance(other, (int, float)):
            return Vector(self[0]*other, self[1]*other, self[2]*other)
        else:
            return NotImplemented

    def __rmul__(self, other):
        """b * a: Scalar multiplication"""
        if isinstance(other, (int, float)):
            return Vector(other*self[0], other*self[1], other*self[2])
        else:
            return NotImplemented

    def __neg__(self):
        """-a: Negation"""
        return Vector(-self[0], -self[1], -self[2])

    def __or__(self, other):
        """a | b: Dot product"""
        if isinstance(other, (tuple, list)) and len(other) >= 3:
            return self[0]*other[0] + self[1]*other[1] + self[2]*other[2]
        else:
            return NotImplemented

    def __ror__(self, other):
        """b | a: Dot product"""
        if isinstance(other, (tuple, list)) and len(other) >= 3:
            return other[0]*self[0] + other[1]*self[1] + other[2]*self[2]
        else:
            return NotImplemented

    def __sub__(self, other):
        """a - b: Vector subtraction"""
        if isinstance(other, (tuple, list)) and len(other) >= 3:
            return Vector(self[0]-other[0], self[1]-other[1], self[2]-other[2])
        else:
            return NotImplemented

    def __rsub__(self, other):
        """b - a: Vector subtraction"""
        if isinstance(other, (tuple, list)) and len(other) >= 3:
            return Vector(other[0]-self[0], other[1]-self[1], other[2]-self[2])
        else:
            return NotImplemented

    def __truediv__(self, other):
        """a / b: Scalar division"""
        if isinstance(other, (int, float)):
            return Vector(self[0]/other, self[1]/other, self[2]/other)
        else:
            return NotImplemented

    def __xor__(self, other):
        """a ^ b: Vector cross product"""
        if isinstance(other, (tuple, list)) and len(other) >= 3:
            return Vector(self[1]*other[2] - self[2]*other[1],
                          self[2]*other[0] - self[0]*other[2],
                          self[0]*other[1] - self[1]*other[0])
        else:
            return NotImplemented

    def __rxor__(self, other):
        """b ^ a: Vector cross product"""
        if isinstance(other, (tuple, list)) and len(other) >= 3:
            return Vector(other[1]*self[2] - other[2]*self[1],
                          other[2]*self[0] - other[0]*self[2],
                          other[0]*self[1] - other[1]*self[0])
        else:
            return NotImplemented