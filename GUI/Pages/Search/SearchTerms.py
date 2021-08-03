from pathlib import Path

from GUI import Attributes
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import CifReader
from MofIdentifier.subbuilding import SBUIdentifier


def condense_t(tup):
    l = tup[0]
    if l is None:
        l = ''
    r = tup[1]
    if r is None:
        r = ''
    return f"({l},{r})"


class SearchTerms:
    def __init__(self, ligands=None, excl_ligands=None, elements=None, excl_elements=None, sbus=None,
                 excl_sbus=None, numerical_attr=None, label=''):
        if excl_sbus is None:
            excl_sbus = []
        if sbus is None:
            sbus = []
        if excl_elements is None:
            excl_elements = []
        if excl_ligands is None:
            excl_ligands = []
        if ligands is None:
            ligands = []
        if elements is None:
            elements = []
        if numerical_attr is None:
            numerical_attr = dict()
        self.ligands = ligands
        self.element_symbols = elements
        self.excl_ligands = excl_ligands
        self.excl_element_symbols = excl_elements
        self.sbus = sbus
        self.excl_sbus = excl_sbus
        self.numerical_attr = numerical_attr
        self.label_substring = label

    def passes(self, MOF):
        if MOF is None or MOF.get_mof() is None:
            return False
        for element in self.element_symbols:
            if element not in MOF.elements_present:
                return False
        for element in self.excl_element_symbols:
            if element in MOF.elements_present:
                return False
        for attr_name in self.numerical_attr:
            if self.numerical_attr[attr_name][0] is not None:
                if Attributes.attributes[attr_name].calculate(MOF) < self.numerical_attr[attr_name][0]:
                    return False  # Less than the minimum
            if self.numerical_attr[attr_name][1] is not None:
                if Attributes.attributes[attr_name].calculate(MOF) > self.numerical_attr[attr_name][1]:
                    return False  # More than the maximum
        if MOF.filename.find(self.label_substring) < 0:
            return False
        if all(sbu.label in MOF.sbu_names for sbu in self.sbus) and \
                not any(sbu.label in MOF.sbu_names for sbu in self.excl_sbus):
            pass
        else:
            return False
        if all(ligand.label in MOF.ligand_names for ligand in self.ligands) and \
                not any(ligand.label in MOF.ligand_names for ligand in self.excl_ligands):
            pass
        else:
            return False
        return True

    def __str__(self):
        ligands = [ligand.name for ligand in self.ligands]
        excl_ligands = [ligand.name for ligand in self.excl_ligands]
        sbus = [sbu.name for sbu in self.sbus]
        excl_sbus = [sbu.name for sbu in self.excl_sbus]
        return f"lig:{ligands}-{excl_ligands}, " + \
               f"elem:{self.element_symbols}-{self.excl_element_symbols}" + \
               f"sbus:{sbus}-{excl_sbus}" + \
               f"attr:{[str(Attributes.attributes[item[0]].index) + condense_t(item[1]) for item in self.numerical_attr.items()]}" + \
               f"n:{self.label_substring}"

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))


def search_in_mofsForGUI_temp(search):
    path = str(Path(__file__).parent / "../../mofsForGUI_temp")
    mofs = CifReader.get_all_mofs_in_directory(path)
    good_mofs = [mof for mof in mofs if search.passes(mof)]
    return good_mofs