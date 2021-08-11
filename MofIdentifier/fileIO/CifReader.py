import os
from io import FileIO, StringIO
from pathlib import Path

from CifFile import ReadCif

from MofIdentifier.Molecules.MOF import MOF
from MofIdentifier.Molecules.atom import Atom


def get_mof(filename):
    mof = read_cif(filename)
    return mof


def get_all_mofs_in_directory(mofs_path):
    mofs = []
    # Change the directory
    original_path = os.getcwd()
    os.chdir(mofs_path)

    for file_name in os.listdir(mofs_path):
        # Check whether file is in text format or not
        if file_name.endswith(".cif"):
            try:
                filepath = Path(file_name).resolve()
                mof = get_mof(str(filepath))
                mofs.append(mof)
            except InterruptedError:
                raise InterruptedError
            except Exception:
                print("Error reading file: ", file_name)
                print(Exception)
    # Return to original directory
    os.chdir(original_path)
    return mofs


def read_cif(filename):
    with FileIO(filename, 'rb') as io:
        cf = ReadCif(io)
        file = open(filename)
        file_str = file.read()
        file.close()
    return mof_from_cf(cf, filename, file_str)


def read_string(cif_content, filename):
    with StringIO(cif_content) as io:
        cf = ReadCif(io)
    return mof_from_cf(cf, filename, cif_content)


def mof_from_cf(cf, filename, file_str):
    cb = cf.first_block()
    file_path = filename
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

    atom_data_loop = cb.GetLoop('_atom_site_label')
    atoms = list(())
    for atomData in atom_data_loop:
        # Modulus 1 to account for edge-case cif files with fractional values v where v < 0 or v > 1
        a = float(atomData._atom_site_fract_x) % 1
        a += 1 if a < 0 else 0
        b = float(atomData._atom_site_fract_y) % 1
        b += 1 if b < 0 else 0
        c = float(atomData._atom_site_fract_z) % 1
        c += 1 if c < 0 else 0
        atom = Atom.from_fractional(atomData._atom_site_label,
                                    atomData._atom_site_type_symbol,
                                    a, b, c, (angle_alpha, angle_beta, angle_gamma), (length_a, length_b, length_c))
        atoms.append(atom)
    return MOF(file_path, atoms, symmetry, length_a, length_b, length_c, angle_alpha, angle_beta, angle_gamma, file_str)


if __name__ == '__main__':
    # uses https://pypi.org/project/PyCifRW/4.3/#description to read CIF files
    MOF = get_mof(r'/Users/davidl/Desktop/Work/2019-11-01-ASR-public_12020/structure_10143/CURYOE01_clean.cif')

    print(MOF.unit_volume)
    print(MOF.cartesian_lengths[0] * MOF.cartesian_lengths[1] * MOF.cartesian_lengths[2])
    print(MOF.sbus().clusters[0])
