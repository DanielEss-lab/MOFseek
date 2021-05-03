class Atom:
    def __init__(self, label, type_symbol, x, y, z):
        self.label = label
        self.type_symbol = type_symbol
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

    def __eq__(self, other):
        return self.label == other.label

    def __hash__(self):
        return hash(self.label)

    def copy_to_relative_position(self, dx, dy, dz):
        atom = Atom(self.label, self.type_symbol, self.x + dx, self.y + dy, self.z + dz)
        atom.isInUnitCell = False
        atom.bondedAtoms = self.bondedAtoms
        return atom
