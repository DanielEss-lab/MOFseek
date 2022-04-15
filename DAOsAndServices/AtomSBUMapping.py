from DAOsAndServices import SBUDAO
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.subbuilding.SBUIdentifier import split


def atom_sbu_mapping(db_mof):
    all_sbus_collection = split(db_mof.get_mof(), show_duplicates=True)
    all_sbus = all_sbus_collection.clusters + all_sbus_collection.connectors + all_sbus_collection.auxiliaries

    sbu_of_atom = dict()
    for sbu in all_sbus:
        for atom in sbu.atoms:
            sbu_of_atom[atom.label] = sbu

    sbu_name_of_sbu = dict()
    for sbu_name in db_mof.sbu_names:
        db_sbu = SBUDAO.get_sbu(sbu_name)
        for sbu in all_sbus:
            if str(sbu.type) == db_sbu.type and SubGraphMatcher.match(sbu, db_sbu.get_sbu()):
                sbu_name_of_sbu[sbu] = sbu_name

    csv_lines = ["atom label, bonded atoms, SBU assigned"]
    for atom in db_mof.get_mof().atoms:
        csv_lines.append(f"{atom.label}, {' '.join(atom.label for atom in atom.bondedAtoms)}, "
                         f"{sbu_name_of_sbu.get(sbu_of_atom[atom.label])}")
    return "\n".join(csv_lines)

