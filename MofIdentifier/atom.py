class Atom:
    def __init__(self, label, type_symbol, x, y, z, isFractional = False):
        self.label = label
        self.type_symbol = type_symbol
        if isFractional:
            self.a = x
            self.b = y
            self.c = z
        else:
            self.x = x
            self.y = y
            self.z = z
        self.bondedAtoms = list(())
        self.isInUnitCell = True

    def __str__(self):
        bonds_string = ''
        for atom in self.bondedAtoms:
            bonds_string = bonds_string + atom.label + ', '
        return "{name} at {x:.1f}, {y:.1f}, {z:.1f} bonded to {bonds}".format(name=self.label, x=self.x, y=self.y,
                                                                              z=self.z, bonds=bonds_string)

    def copy_to_relative_position(self, da, db, dc, mof):
        atom = Atom(self.label, self.type_symbol, self.a + da, self.b + db, self.c + dc, isFractional=True)
        (atom.x, atom.y, atom.z) = mof.conversion_to_Cartesian(atom)
        atom.isInUnitCell = False
        atom.bondedAtoms = self.bondedAtoms
        return atom
