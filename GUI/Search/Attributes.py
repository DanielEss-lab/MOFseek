class Attribute:
    def __init__(self, description, calculate, enabled):
        self.description = description
        self.calculate = calculate
        self.enabled = enabled


attributes = {
    "Volume (\u212B\u00B3)": Attribute("The volume of the MOF's unit cell, measured in Angstroms cubed",
                                       lambda mof: round(mof.unit_volume, 0), True),
    "\u0394Length (\u212B):": Attribute("The difference between the MOF's unit cell's longest length and shortest "
                                        "length (measured in Angstroms, in cartesian coordinates)",
                                        lambda mof: round(max(mof.cartesian_lengths) - min(mof.cartesian_lengths), 2),
                                        True),
    "\u0394Angle (\u00B0)": Attribute("The difference between the MOF's unit cell's greatest angle and shortest angle "
                                      "(in degrees)",
                                      lambda mof: round(max(mof.angles) - min(mof.angles), 2), True),
    "Num Atoms": Attribute("The number of atoms in the MOF's unit cell",
                           lambda mof: len(mof.atoms), True),
    "conn atms/node atm": Attribute("The ratio within the MOF of atoms in connecting ligands vs atoms in metal nodes",
                                    lambda mof: round(mof.sbus().num_connector_atoms / mof.sbus().num_cluster_atoms, 2),
                                    True),
    "Aux/\u212B\u00B3": Attribute("The density of auxiliary groups in the MOF, measured in groups/Angstroms cubed",
                                  lambda mof: round(len(mof.sbus().auxiliaries) / mof.unit_volume, 5), True),
    "avg conn *": Attribute("The MOF's average connectivity of connecting ligands, ie how many nodes each one connects",
                            lambda mof: round(mof.sbus().avg_conn_connectivity, 1), True),
    "avg node *": Attribute("The MOF's average connectivity of metal nodes, ie how many connecting ligands each one "
                            "touches",
                            lambda mof: round(mof.sbus().avg_node_connectivity, 1), True),
}
