import itertools


class Attribute:
    id_iter = itertools.count()

    def __init__(self, description, calculate, enabled):
        self.description = description
        self.calculate = calculate
        self.enabled = enabled
        self.index = next(Attribute.id_iter)


attributes = {
    "\u2113 x(\u212B)": Attribute("The length, measured in Angstroms, of the MOF's 'x' dimension in cartesian "
                                  "coordinates",
                                  lambda mof: round(mof.cartesian_lengths[0], 1), False),
    "\u2113 y(\u212B)": Attribute("The length, measured in Angstroms, of the MOF's 'y' dimension in cartesian "
                                  "coordinates",
                                  lambda mof: round(mof.cartesian_lengths[1], 1), False),
    "\u2113 z(\u212B)": Attribute("The length, measured in Angstroms, of the MOF's 'z' dimension in cartesian "
                                  "coordinates",
                                  lambda mof: round(mof.cartesian_lengths[2], 1), False),
    "Volume (\u212B\u00B3)": Attribute("The volume of the MOF's unit cell, measured in Angstroms cubed",
                                       lambda mof: round(mof.unit_volume, 0), True),
    "\u2113 a(\u212B)": Attribute("The length, measured in Angstroms, of the MOF's unit cell's edge labelled 'a'",
                                  lambda mof: round(mof.fractional_lengths[0], 1), False),
    "\u2113 b(\u212B)": Attribute("The length, measured in Angstroms, of the MOF's unit cell's edge labelled 'b'",
                                  lambda mof: round(mof.fractional_lengths[1], 1), False),
    "\u2113 c(\u212B)": Attribute("The length, measured in Angstroms, of the MOF's unit cell's edge labelled 'c'",
                                  lambda mof: round(mof.fractional_lengths[2], 1), False),
    "\u0394\u2113 (\u212B):": Attribute("The difference between the MOF's unit cell's longest length and shortest "
                                        "length (measured in Angstroms, in cartesian coordinates)",
                                        lambda mof: round(max(mof.cartesian_lengths) - min(mof.cartesian_lengths), 2),
                                        True),
    "\u2220 \u03B1(\u00B0)": Attribute("The angle, measured in degrees, of the MOF's unit cell's angle designated as "
                                       "'alpha'",
                                       lambda mof: round(mof.angles[0], 2), False),
    "\u2220 \u03B2(\u00B0)": Attribute("The angle, measured in degrees, of the MOF's unit cell's angle designated as "
                                       "'beta'",
                                       lambda mof: round(mof.angles[1], 2), False),
    "\u2220 \u03B3(\u00B0)": Attribute("The angle, measured in degrees, of the MOF's unit cell's angle designated as "
                                       "'gamma'",
                                       lambda mof: round(mof.angles[2], 2), False),
    "\u0394\u2220 (\u00B0)": Attribute("The difference between the MOF's unit cell's greatest angle and shortest angle "
                                       "(in degrees)",
                                       lambda mof: round(max(mof.angles) - min(mof.angles), 2), True),
    "Num Atoms": Attribute("The number of atoms in the MOF's unit cell",
                           lambda mof: mof.num_atoms, True),
    "Conn/Node A": Attribute("The ratio within the MOF of atoms in connecting ligands vs atoms in metal nodes",
                             lambda mof: round(mof.conn_node_atom_ratio, 2), True),
    "Aux/\u212B\u00B3": Attribute("The density of auxiliary groups in the MOF, measured in groups/Angstroms cubed",
                                  lambda mof: round(mof.aux_density, 5), True),
    "Avg Conn *": Attribute("The MOF's average connectivity of connecting ligands, ie how many nodes each one connects",
                            lambda mof: round(mof.conn_connectivity, 1), True),
    "Avg Node *": Attribute("The MOF's average connectivity of metal nodes, ie how many connecting ligands each one "
                            "touches",
                            lambda mof: round(mof.node_connectivity, 1), True),
}
