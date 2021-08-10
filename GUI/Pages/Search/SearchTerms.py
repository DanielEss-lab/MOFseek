from pathlib import Path

from GUI import Attributes, Settings
from MofIdentifier.fileIO import CifReader


def condense_t(tup):
    if tup is None:
        return '-'
    if isinstance(tup, bool):
        return 'Y' if tup else 'N'
    l = tup[0]
    if l is None:
        l = ''
    r = tup[1]
    if r is None:
        r = ''
    return f"({l},{r})"


class SearchTerms:
    def __init__(self, ligands=None, excl_ligands=None, elements=None, excl_elements=None, sbus=None,
                 excl_sbus=None, attr=None, label=''):
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
        if attr is None:
            attr = dict()
        self.ligand_names = ligands
        self.element_symbols = elements
        self.excl_ligand_names = excl_ligands
        self.excl_element_symbols = excl_elements
        self.sbu_names = sbus
        self.excl_sbu_names = excl_sbus
        self.attr = attr
        self.label_substring = label

    def passes(self, MOF):
        if MOF is None or MOF.get_mof() is None:
            return False
        if MOF.disorder and not Settings.allow_disorder:
            return False
        for element in self.element_symbols:
            if element not in MOF.elements_present:
                return False
        for element in self.excl_element_symbols:
            if element in MOF.elements_present:
                return False
        for attr_name in self.attr:
            attr = Attributes.attributes[attr_name]
            if attr.var_type is bool:
                if self.attr[attr_name] is not None:
                    if self.attr[attr_name] != attr.calculate(MOF):
                        # If SearchTerms requires false and it calculates to true, or vice versa
                        return False
            elif attr.var_type is str:
                if self.attr[attr_name][0] is not None:  # exclusion string
                    if self.attr[attr_name][0] in attr.calculate(MOF):
                        return False
                if self.attr[attr_name][1] is not None:  # inclusion string
                    if not self.attr[attr_name][1] in attr.calculate(MOF):
                        return False
            else:
                if self.attr[attr_name][0] is not None:
                    if attr.calculate(MOF) < self.attr[attr_name][0]:
                        return False  # Less than the minimum
                if self.attr[attr_name][1] is not None:
                    if attr.calculate(MOF) > self.attr[attr_name][1]:
                        return False  # More than the maximum
        if MOF.filename.find(self.label_substring) < 0:
            return False
        if all(name in MOF.sbu_names for name in self.sbu_names) and \
                not any(name in MOF.sbu_names for name in self.excl_sbu_names):
            pass
        else:
            return False
        if all(name in MOF.ligand_names for name in self.ligand_names) and \
                not any(name in MOF.ligand_names for name in self.excl_ligand_names):
            pass
        else:
            return False
        return True

    def __str__(self):
        return f"lig:{self.ligand_names}-{self.excl_ligand_names}, " + \
               f"elem:{self.element_symbols}-{self.excl_element_symbols}" + \
               f"sbus:{self.sbu_names}-{self.excl_sbu_names}" + \
               f"attr:{[str(Attributes.attributes[item[0]].index) + condense_t(item[1]) for item in self.attr.items()]}" + \
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