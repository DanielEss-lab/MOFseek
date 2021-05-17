from CifFile import ReadCif

from MofIdentifier.MOF import MOF
from MofIdentifier.atom import Atom
from MofIdentifier.MofBondCreator import MofBondCreator


def get_mof(filename):
    mof = read_cif(filename)
    bond_creator = MofBondCreator(mof)
    bond_creator.connect_atoms()
    return mof


def read_cif(filename):
    cf = ReadCif(filename)
    cb = cf.first_block()
    label = filename
    try:
        symmetry = cb['_symmetry_cell_setting']
    except KeyError:
        symmetry = None
    length_a = float(cb['_cell_length_a'])
    length_b = float(cb['_cell_length_b'])
    length_c = float(cb['_cell_length_c'])
    angle_alpha = float(cb['_cell_angle_alpha'])
    angle_beta = float(cb['_cell_angle_beta'])
    angle_gamma = float(cb['_cell_angle_gamma'])

    mof = MOF(label, symmetry, length_a, length_b, length_c, angle_alpha, angle_beta, angle_gamma)

    atom_data_loop = cb.GetLoop('_atom_site_label')
    atoms = list(())
    for atomData in atom_data_loop:
        a = float(atomData._atom_site_fract_x)
        a += 1 if a < 0 else 0
        b = float(atomData._atom_site_fract_y)
        b += 1 if b < 0 else 0
        c = float(atomData._atom_site_fract_z)
        c += 1 if c < 0 else 0
        atom = Atom.from_fractional(atomData._atom_site_label,
                                    atomData._atom_site_type_symbol,
                                    a, b, c, mof)
        atoms.append(atom)
    mof.set_atoms(atoms)
    return mof


if __name__ == '__main__':
    # uses https://pypi.org/project/PyCifRW/4.3/#description to read CIF files
    MOF_808 = get_mof('mofsForTests/smod7-pos-1.cif')

    print(MOF_808)
    print(*MOF_808.elementsPresent)
