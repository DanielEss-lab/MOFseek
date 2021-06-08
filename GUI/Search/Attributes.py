attribute_names = [
            "Volume (A^3)",
            "\u0394Length (A):",
            "\u0394Angle (\u00B0)",
            "Num Atoms",
            "conn atoms/node atoms",
            "Aux/Vol",
            "avg conn\u00B0",
            "avg node\u00B0",
        ]


def get_attributes(mof):
    return {
        attribute_names[0]: round(mof.length_x * mof.length_y * mof.length_z, 0),
        attribute_names[1]: round(max(mof.length_x, mof.length_y, mof.length_z) -
                                   min(mof.length_x, mof.length_y, mof.length_z), 2),
        attribute_names[2]: round(max(mof.angle_alpha, mof.angle_beta, mof.angle_gamma) -
                                      min(mof.angle_alpha, mof.angle_beta, mof.angle_gamma), 2),
        attribute_names[3]: len(mof.atoms),
        attribute_names[4]: round(mof.sbu_split.num_connector_atoms / mof.sbu_split.num_cluster_atoms, 2),
        attribute_names[5]: round(len(mof.sbu_split.auxiliaries) / (mof.length_x * mof.length_y * mof.length_z), 5),  # FIXME
        attribute_names[6]: round(mof.sbu_split.avg_conn_connectivity, 1),  # degree?
        attribute_names[7]: round(mof.sbu_split.avg_node_connectivity, 1),
    }