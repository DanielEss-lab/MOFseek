attribute_names = [
            "Volume (\u212B^3)",
            "\u0394Length (\u212B):",
            "\u0394Angle (\u00B0)",
            "Num Atoms",
            "conn atms/node atm",
            "Aux/Vol",
            "avg conn\u00B0",  # degree
            "avg node\u00B0",
        ]


attribute_descriptions = {
        attribute_names[0]: "The volume of the MOF's unit cell, measured in Angstroms cubed",
        attribute_names[1]: "The difference between the MOF's unit cell's longest length and shortest length "
                            "(measured in Angstroms, in cartesian coordinates)",
        attribute_names[2]: "The difference between the MOF's unit cell's greatest angle and shortest angle (in "
                            "degrees)",
        attribute_names[3]: "The number of atoms in the MOF's unit cell",
        attribute_names[4]: "The ratio within the MOF of atoms in connecting ligands vs atoms in metal nodes",
        attribute_names[5]: "The density of auxiliary groups in the MOF, measured in groups/Angstrom cubed",
        attribute_names[6]: "The MOF's average connectivity of connecting ligands, ie how many nodes each one connects",
        attribute_names[7]: "The MOF's average connectivity of metal nodes, ie how many connecting ligands each one "
                            "touches",
}


def get_attributes(mof):
    return {
        attribute_names[0]: round(mof.length_x * mof.length_y * mof.length_z, 0),
        attribute_names[1]: round(max(mof.length_x, mof.length_y, mof.length_z) -
                                   min(mof.length_x, mof.length_y, mof.length_z), 2),
        attribute_names[2]: round(max(mof.angle_alpha, mof.angle_beta, mof.angle_gamma) -
                                      min(mof.angle_alpha, mof.angle_beta, mof.angle_gamma), 2),
        attribute_names[3]: len(mof.atoms),
        attribute_names[4]: round(mof.sbu_split.num_connector_atoms / mof.sbu_split.num_cluster_atoms, 2),
        attribute_names[5]: round(len(mof.sbu_split.auxiliaries) / (mof.length_x * mof.length_y * mof.length_z), 5),
        attribute_names[6]: round(mof.sbu_split.avg_conn_connectivity, 1),
        attribute_names[7]: round(mof.sbu_split.avg_node_connectivity, 1),
    }