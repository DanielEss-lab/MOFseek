import itertools


class Attribute:
    id_iter = itertools.count()

    def __init__(self, description, calculate, enabled, var_type):
        self.description = description
        self.calculate = calculate
        self.enabled = enabled
        self.index = next(Attribute.id_iter)
        self.var_type = var_type


attributes = {
    "\u2113 x(\u212B)": Attribute("The length, measured in Angstroms, of the MOF's 'x' dimension in cartesian "
                                  "coordinates",
                                  lambda mof: round(mof.cartesian_lengths[0], 1), False, float),
    "\u2113 y(\u212B)": Attribute("The length, measured in Angstroms, of the MOF's 'y' dimension in cartesian "
                                  "coordinates",
                                  lambda mof: round(mof.cartesian_lengths[1], 1), False, float),
    "\u2113 z(\u212B)": Attribute("The length, measured in Angstroms, of the MOF's 'z' dimension in cartesian "
                                  "coordinates",
                                  lambda mof: round(mof.cartesian_lengths[2], 1), False, float),
    "Volume (\u212B\u00B3)": Attribute("The volume of the MOF's unit cell, measured in Angstroms cubed",
                                       lambda mof: round(mof.unit_volume, 0), True, float),
    "\u2113 a(\u212B)": Attribute("The length, measured in Angstroms, of the MOF's unit cell's edge labelled 'a'",
                                  lambda mof: round(mof.fractional_lengths[0], 1), False, float),
    "\u2113 b(\u212B)": Attribute("The length, measured in Angstroms, of the MOF's unit cell's edge labelled 'b'",
                                  lambda mof: round(mof.fractional_lengths[1], 1), False, float),
    "\u2113 c(\u212B)": Attribute("The length, measured in Angstroms, of the MOF's unit cell's edge labelled 'c'",
                                  lambda mof: round(mof.fractional_lengths[2], 1), False, float),
    "\u0394\u2113 (\u212B):": Attribute("The difference between the MOF's unit cell's longest length and shortest "
                                        "length (measured in Angstroms, in cartesian coordinates)",
                                        lambda mof: round(max(mof.cartesian_lengths) - min(mof.cartesian_lengths), 2),
                                        False, float),
    "\u2220 \u03B1(\u00B0)": Attribute("The angle, measured in degrees, of the MOF's unit cell's angle designated as "
                                       "'alpha'",
                                       lambda mof: round(mof.angles[0], 2), False, float),
    "\u2220 \u03B2(\u00B0)": Attribute("The angle, measured in degrees, of the MOF's unit cell's angle designated as "
                                       "'beta'",
                                       lambda mof: round(mof.angles[1], 2), False, float),
    "\u2220 \u03B3(\u00B0)": Attribute("The angle, measured in degrees, of the MOF's unit cell's angle designated as "
                                       "'gamma'",
                                       lambda mof: round(mof.angles[2], 2), False, float),
    "\u0394\u2220 (\u00B0)": Attribute("The difference between the MOF's unit cell's greatest angle and shortest angle "
                                       "(in degrees)",
                                       lambda mof: round(max(mof.angles) - min(mof.angles), 2), False, float),
    "Num Atoms": Attribute("The number of atoms in the MOF's unit cell",
                           lambda mof: mof.num_atoms, True, int),
    "Conn/Node A": Attribute("The ratio within the MOF of atoms in connecting ligands vs atoms in metal nodes",
                             lambda mof: round(mof.conn_node_atom_ratio, 2), False, float),
    "Aux/\u212B\u00B3": Attribute("The density of auxiliary groups in the MOF, measured in groups/Angstroms cubed",
                                  lambda mof: round(mof.aux_density, 5), True, float),
    "Avg Conn *": Attribute("The MOF's average connectivity of connecting ligands, ie how many nodes each one connects",
                            lambda mof: round(mof.conn_connectivity, 1), False, float),
    "Avg Node *": Attribute("The MOF's average connectivity of metal nodes, ie how many connecting ligands each one "
                            "touches",
                            lambda mof: round(mof.node_connectivity, 1), False, float),
    "LCD": Attribute("Largest Cavity Diameter", lambda mof: round(mof.LCD, 3) if mof.LCD is not None else None, True, float),
    "PLD": Attribute("Pore Limiting Diameter", lambda mof: round(mof.PLD, 3) if mof.PLD is not None else None, True, float),
    "LFPD": Attribute("Largest Sphere along the Free Path", lambda mof: round(mof.LFPD, 3) if mof.LFPD is not None else None, True, float),
    # "cm3_g": Attribute("density", lambda mof: round(mof.cm3_g, 3) if mof.cm3_g is not None else None, True, float),
    "ASA_m2_cm3": Attribute("Accessible Surface Area", lambda mof: round(mof.ASA_m2_cm3, 3) if mof.ASA_m2_cm3 is not None else None, False, float),
    "ASA_m2_g": Attribute("Accessible Surface Area", lambda mof: round(mof.ASA_m2_g, 3) if mof.ASA_m2_g is not None else None, False, float),
    "NASA_m2_cm3": Attribute("Non-Accessible Surface Area", lambda mof: round(mof.NASA_m2_cm3, 3) if mof.NASA_m2_cm3 is not None else None, False, float),
    "NASA_m2_g": Attribute("Non-Accessible Surface Area", lambda mof: round(mof.NASA_m2_g, 3) if mof.NASA_m2_g is not None else None, False, float),
    "AV_VF": Attribute("Void Fraction, 0-1", lambda mof: round(mof.AV_VF, 3) if mof.AV_VF is not None else None, False, float),
    # "AV_cm3_g": Attribute("Void Fraction, 0-1", lambda mof: round(mof.AV_cm3_g, 3) if mof.AV_cm3_g is not None else None, False, float),
    "NAV_cm3_g": Attribute("Non-Accessible Volume", lambda mof: round(mof.NAV_cm3_g, 7) if mof.NAV_cm3_g is not None else None, False, float),
    "Has_OMS": Attribute("Has Open Metal Sites", lambda mof: mof.Has_OMS, False, bool),  # Boolean
    "OMS": Attribute("Open Metal Sites", lambda mof: str(mof.Open_Metal_Sites)[1:-1] if mof.Open_Metal_Sites is not None else None, False, str),  # could be list of str
    # "Extension": Attribute("Last bit of filename", lambda mof: mof.Extension, False, str),  # str
    # "FSR_overlap": Attribute("Unknown acronym", lambda mof: mof.FSR_overlap, False, bool),  # Boolean
    # "from_CSD": Attribute("Unknown acronym", lambda mof: mof.from_CSD, False, bool),  # Boolean
    # "public": Attribute("Unknown meaning", lambda mof: mof.public, False, bool),
    # "DISORDER": Attribute("If this value is True, then the mof comes from unreliable data, and its structural "
    #                       "calculations may be inaccurate.", lambda mof: mof.public, False, bool),  # Boolean. Should, by default, not allow them AND not show this attribute.
    # "CSD_overlap": Attribute("CSD overlap in CoRE database", lambda mof: mof.CSD_overlap_inCoRE, False, bool),  # Boolean
    # "CSD_of_WoS": Attribute("CSD of WoS in CoRE", lambda mof: mof.CSD_of_WoS_inCoRE, False, bool),
    # "date_CSD": Attribute("unknown meaning", lambda mof: mof.date_CSD, False, str),  # str
    # "DOI_public": Attribute("unknown meaning", lambda mof: mof.DOI_public, False, str),  # str
    # "Note": Attribute("unknown meaning", lambda mof: mof.Note, False, str),  # str TODO: change this to has_note, display note in MOFView
    # "Matched_CSD_of_CoRE": Attribute("unknown meaning", lambda mof: mof.Matched_CSD_of_CoRE, False, str),  # str
    # "Possible_List_CSD_of_CoRE": Attribute("unknown meaning", lambda mof: mof.Possible_List_CSD_of_CoRE, False, str),  # str
}
