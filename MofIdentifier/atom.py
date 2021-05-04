class Atom:
    def __init__(self, label, type_symbol, x, y, z, is_fractional=False):
        self.label = label
        self.type_symbol = type_symbol
        if is_fractional:
            self.a = x
            self.b = y
            self.c = z
        else:
            self.x = x
            self.y = y
            self.z = z
        self.bondedAtoms = list(())
        self.isInUnitCell = True

    @classmethod
    def from_cartesian(cls, label, type_symbol, x, y, z):
        return cls(label, type_symbol, x, y, z)

    @classmethod
    def from_fractional(cls, label, type_symbol, a, b, c, mof):
        atom = cls(label, type_symbol, a, b, c, is_fractional=True)
        (atom.x, atom.y, atom.z) = mof.conversion_to_Cartesian(atom)
        return atom

    def __str__(self):
        bonds_string = ''
        for atom in self.bondedAtoms:
            bonds_string = bonds_string + atom.label + ', '
        return "{name} at {x:.1f}, {y:.1f}, {z:.1f} bonded to {bonds}".format(name=self.label, x=self.x, y=self.y,
                                                                              z=self.z, bonds=bonds_string)

    def __eq__(self, other):
        return self.label == other.label

    def __hash__(self):
        return hash(self.label)

    def copy_to_relative_position(self, da, db, dc, mof):
        atom = Atom.from_fractional(self.label, self.type_symbol, self.a + da, self.b + db, self.c + dc, mof)
        atom.isInUnitCell = False
        atom.bondedAtoms = self.bondedAtoms
        return atom
