from DAO import MOFDAO, LigandDAO
from MofIdentifier.fileIO import CifReader


class ContainedSBU:
    def __init__(self, info_string):
        self.frequency, self.connectivity, self.name = info_string.split(' ', 2)


def try_float(v):
    try:
        return float(v)
    except TypeError:
        return None


class MOFDatabase:
    def __init__(self, dictionary):
        self.filename = dictionary['filename']
        self._mof = None
        try:
            self.simple_initialize(dictionary)
        except (KeyError, ValueError):
            self.complex_initialize(dictionary)

    def simple_initialize(self, dictionary):
        self.file_content = dictionary['cif_content']
        self.symmetry = dictionary['symmetry']
        self.fractional_lengths = dictionary['fractional_lengths']
        self.angles = dictionary['angles']
        self.unit_volume = dictionary['unit_volume']
        self.cartesian_lengths = dictionary['cartesian_lengths']
        self.elementsPresent = dictionary['elementsPresent']
        self.atoms_string_with_solvents = dictionary['atoms_string_with_solvents']
        self.atoms_string_without_solvents = dictionary['atoms_string_without_solvents']
        self.ligand_names = dictionary['ligand_names']
        sbu_node_info = dictionary['sbu_node_info']
        self.sbu_nodes = [ContainedSBU(info) for info in sbu_node_info]
        sbu_conn_info = dictionary['sbu_conn_info']
        self.sbu_connectors = [ContainedSBU(info) for info in sbu_conn_info]
        sbu_aux_info = dictionary['sbu_aux_info']
        self.sbu_auxiliaries = [ContainedSBU(info) for info in sbu_aux_info]
        self.sbu_names = [SBU.name for SBU in self.sbu_nodes]
        self.sbu_names.extend([SBU.name for SBU in self.sbu_connectors])
        self.sbu_names.extend([SBU.name for SBU in self.sbu_auxiliaries])

        self.LCD = float(dictionary['LCD'])
        self.PLD = float(dictionary['PLD'])
        self.LFPD = float(dictionary['LFPD'])
        self.cm3_g = float(dictionary['cm3_g'])
        self.ASA_m2_cm3 = float(dictionary['ASA_m2_cm3'])
        self.ASA_m2_g = float(dictionary['ASA_m2_g'])
        self.NASA_m2_cm3 = float(dictionary['NASA_m2_cm3'])
        self.NASA_m2_g = float(dictionary['NASA_m2_g'])
        self.AV_VF = float(dictionary['AV_VF'])
        self.AV_cm3_g = float(dictionary['AV_cm3_g'])
        self.NAV_cm3_g = float(dictionary['NAV_cm3_g'])
        # self.All_Metals = dictionary.get('All_Metals')  # Not relevant, but perhaps we'll want to add it back someday
        self.Has_OMS = True if dictionary['Has_OMS'] == 'Yes' else False
        open_sites = dictionary['Open_Metal_Sites']
        self.Open_Metal_Sites = [] if open_sites is None else open_sites.split(',')
        self.Extension = dictionary.get('Extension')
        self.FSR_overlap = True if dictionary.get('FSR_overlap') == 'Y' else False
        self.from_CSD = True if dictionary.get('from_CSD') == 'Y' else False
        self.public = True if dictionary.get('public') == 'Y' else False
        self.DISORDER = True if dictionary.get('DISORDER') == 'DISORDER' else False
        self.CSD_overlap_inCoRE = True if dictionary.get('CSD_overlap_inCoRE') == 'Y' else False
        self.CSD_of_WoS_inCoRE = dictionary.get('CSD_of_WoS_inCoRE')
        CSD_o_inCCDC = dictionary.get('CSD_overlap_inCCDC')
        self.CSD_overlap_inCCDC = True if CSD_o_inCCDC == 'Y' else False if CSD_o_inCCDC == 'N' else CSD_o_inCCDC
        self.date_CSD = dictionary.get('date_CSD')
        self.DOI_public = dictionary.get('DOI_public')
        self.Note = dictionary.get('Note')
        self.Matched_CSD_of_CoRE = dictionary.get('Matched_CSD_of_CoRE')
        self.Possible_List_CSD_of_CoRE = dictionary.get('Possible_List_CSD_of_CoRE')

        self.num_atoms = dictionary['num_atoms']
        self.conn_node_atom_ratio = dictionary['conn_node_atom_ratio']
        self.aux_density = dictionary['aux_density']
        self.conn_connectivity = dictionary['conn_connectivity']
        self.node_connectivity = dictionary['node_connectivity']
        self.elements_present = dictionary['elements_present']

    def complex_initialize(self, dictionary):
        try:
            self.file_content = dictionary['cif_content']
        except KeyError:
            self.file_content = None

        self.set_from_dictionary_or_mof('symmetry', dictionary)
        self.set_from_dictionary_or_mof('fractional_lengths', dictionary)
        self.set_from_dictionary_or_mof('angles', dictionary)
        self.set_from_dictionary_or_mof('unit_volume', dictionary)
        self.set_from_dictionary_or_mof('cartesian_lengths', dictionary)
        self.set_from_dictionary_or_mof('elementsPresent', dictionary)
        self.atoms_string_with_solvents = self.get_or_calculate('atoms_string_with_solvents',
                                                           lambda mof: mof.atoms_string_with_solvents(), dictionary)
        self.atoms_string_without_solvents = self.get_or_calculate('atoms_string_without_solvents',
                                                           lambda mof: mof.atoms_string_without_solvents(), dictionary)

        self.ligand_names = self.get_or_calculate('ligand_names', lambda mof: LigandDAO.scan_all_for_mof(mof), dictionary)
        if self.get_mof() is not None:
            sbu_node_info = dictionary['sbu_node_info']
            self.sbu_nodes = [ContainedSBU(info) for info in sbu_node_info]
            sbu_conn_info = dictionary['sbu_conn_info']
            self.sbu_connectors = [ContainedSBU(info) for info in sbu_conn_info]
            sbu_aux_info = dictionary['sbu_aux_info']
            self.sbu_auxiliaries = [ContainedSBU(info) for info in sbu_aux_info]
            self.sbu_names = [SBU.name for SBU in self.sbu_nodes]
            self.sbu_names.extend([SBU.name for SBU in self.sbu_connectors])
            self.sbu_names.extend([SBU.name for SBU in self.sbu_auxiliaries])
        else:
            self.sbu_nodes = self.sbu_connectors = self.sbu_auxiliaries = None
            self.sbu_names = []

        self.LCD = try_float(dictionary.get('LCD'))
        self.PLD = try_float(dictionary.get('PLD'))
        self.LFPD = try_float(dictionary.get('LFPD'))
        self.cm3_g = try_float(dictionary.get('cm3_g'))
        self.ASA_m2_cm3 = try_float(dictionary.get('ASA_m2_cm3'))
        self.ASA_m2_g = try_float(dictionary.get('ASA_m2_g'))
        self.NASA_m2_cm3 = try_float(dictionary.get('NASA_m2_cm3'))
        self.NASA_m2_g = try_float(dictionary.get('NASA_m2_g'))
        self.AV_VF = try_float(dictionary.get('AV_VF'))
        self.AV_cm3_g = try_float(dictionary.get('AV_cm3_g'))
        self.NAV_cm3_g = try_float(dictionary.get('NAV_cm3_g'))
        # self.All_Metals = dictionary.get('All_Metals')  # Not relevant, but perhaps we'll want to add it back someday
        self.Has_OMS = True if dictionary.get('Has_OMS') == 'Yes' else False
        open_sites = dictionary.get('Open_Metal_Sites')
        self.Open_Metal_Sites = [] if open_sites is None else open_sites.split(',')
        self.Extension = dictionary.get('Extension')
        self.FSR_overlap = True if dictionary.get('FSR_overlap') == 'Y' else False
        self.from_CSD = True if dictionary.get('from_CSD') == 'Y' else False
        self.public = True if dictionary.get('public') == 'Y' else False
        self.DISORDER = True if dictionary.get('DISORDER') == 'DISORDER' else False
        self.CSD_overlap_inCoRE = True if dictionary.get('CSD_overlap_inCoRE') == 'Y' else False
        self.CSD_of_WoS_inCoRE = dictionary.get('CSD_of_WoS_inCoRE')
        CSD_o_inCCDC = dictionary.get('CSD_overlap_inCCDC')
        self.CSD_overlap_inCCDC = True if CSD_o_inCCDC == 'Y' else False if CSD_o_inCCDC == 'N' else CSD_o_inCCDC
        self.date_CSD = dictionary.get('date_CSD')
        self.DOI_public = dictionary.get('DOI_public')
        self.Note = dictionary.get('Note')
        self.Matched_CSD_of_CoRE = dictionary.get('Matched_CSD_of_CoRE')
        self.Possible_List_CSD_of_CoRE = dictionary.get('Possible_List_CSD_of_CoRE')

        self.num_atoms = self.get_or_calculate('num_atoms', lambda mof: len(mof.atoms), dictionary)
        self.conn_node_atom_ratio = self.get_or_calculate('conn_node_atom_ratio', lambda mof:
                mof.sbus().num_connector_atoms / mof.sbus().num_cluster_atoms, dictionary)
        self.aux_density = self.get_or_calculate('aux_density', lambda mof: len(mof.sbus().auxiliaries) / mof.unit_volume, dictionary)
        self.conn_connectivity = self.get_or_calculate('conn_connectivity', lambda mof: mof.sbus().avg_conn_connectivity, dictionary)
        self.node_connectivity = self.get_or_calculate('node_connectivity', lambda mof: mof.sbus().avg_node_connectivity, dictionary)
        self.elements_present = self.get_or_calculate('elements_present', lambda mof: mof.elementsPresent, dictionary)

    def get_mof(self):
        if self._mof is None:
            if self.file_content is not None:
                self._mof = CifReader.read_string(self.file_content, self.filename + '.cif')
            else:
                return None
        return self._mof

    def set_from_dictionary_or_mof(self, attribute_name, dictionary):
        try:
            setattr(self, attribute_name, dictionary[attribute_name])
        except KeyError:
            if self.get_mof() is not None:
                # use cif content to make MOF object, get attribute from that
                value = getattr(self.get_mof(), attribute_name)
                MOFDAO.store_value(self.filename, attribute_name, value)
                setattr(self, attribute_name, value)
            else:
                setattr(self, attribute_name, None)

    def get_or_calculate(self, attribute_name, calculator, dictionary):
        self.yes = True
        try:
            return dictionary[attribute_name]
        except KeyError:
            if self.get_mof() is not None:
                # use cif content to make MOF object, calculate attribute from that
                value = calculator(self.get_mof())
                MOFDAO.store_value(self.filename, attribute_name, value)
                return value
            else:
                return None