class MOF:
    def __init__(self, label, symmetry, a, b, c, al, be, ga, atoms):
        self.label = label
        self.symmetry = symmetry
        self.length_a = a
        self.length_b = b
        self.length_c = c
        self.angle_alpha = al
        self.angle_beta = be
        self.angle_gamma = ga
        self.atoms = atoms

    def __str__(self):
        return "{} with dimensions {}, {}, {}".format(self.label,
                                                      self.length_a, self.length_b, self.length_c)
