from io import StringIO
from MofIdentifier.fileIO import CifReader


class MOFDatabase:
    def __init__(self, dictionary):
        try:
            self.cif_content = dictionary['cif_content']
        except KeyError:
            self.cif_content = None
        self._mof = None

        def set_from_dictionary_or_mof(attribute_name):
            try:
                setattr(self, attribute_name, dictionary['attribute_name'])
            except KeyError:
                if self.cif_content is not None:
                    # use cif content to make MOF object, get attribute from that
                    if self._mof is None:
                        self._mof = CifReader.read_cif(StringIO(self.cif_content))
                    setattr(self, attribute_name, getattr(self._mof, attribute_name))
                else:
                    setattr(self, attribute_name, None)

        set_from_dictionary_or_mof('symmetry')
        set_from_dictionary_or_mof('fractional_lengths')
        set_from_dictionary_or_mof('angles')
        set_from_dictionary_or_mof('unit_volume')
        set_from_dictionary_or_mof('cartesian_lengths')
        set_from_dictionary_or_mof('elementsPresent')
        try:
            self.sbu_names = dictionary['sbu_names']
        except KeyError:
            self.sbu_names = set()
            # TODO: attempt to figure them out by splitting mof and comparing to sbus in database
        self.filename = dictionary['filename']
        self.LCD = dictionary['LCD']
        self.PLD = dictionary['PLD']
        self.LFPD = dictionary['LFPD']
        self.cm3_g = dictionary['cm3_g']
        self.ASA_m2_cm3 = dictionary['ASA_m2_cm3']
        self.ASA_m2_g = dictionary['ASA_m2_g']
        self.NASA_m2_cm3 = dictionary['NASA_m2_cm3']
        self.NASA_m2_g = dictionary['NASA_m2_g']
        self.AV_VF = dictionary['AV_VF']
        self.AV_cm3_g = dictionary['AV_cm3_g']
        self.NAV_cm3_g = dictionary['NAV_cm3_g']
        self.All_Metals = dictionary['All_Metals']
        self.Has_OMS = dictionary['Has_OMS']
        self.Open_Metal_Sites = dictionary['Open_Metal_Sites']
        self.Extension = dictionary['Extension']
        self.FSR_overlap = dictionary['FSR_overlap']
        self.from_CSD = dictionary['from_CSD']
        self.public = dictionary['public']
        self.DISORDER = dictionary['DISORDER']
        self.CSD_overlap_inCoRE = dictionary['CSD_overlap_inCoRE']
        self.CSD_of_WoS_inCoRE = dictionary['CSD_of_WoS_inCoRE']
        self.CSD_overlap_inCCDC = dictionary['CSD_overlap_inCCDC']
        self.date_CSD = dictionary['date_CSD']
        self.DOI_public = dictionary['DOI_public']
        self.Note = dictionary['Note']
        self.Matched_CSD_of_CoRE = dictionary['Matched_CSD_of_CoRE']
        self.Possible_List_CSD_of_CoRE = dictionary['Possible_List_CSD_of_CoRE']
        try:
            self.ligand_names = dictionary['ligand_names']
        except KeyError:
            self.sbu_names = set()

    def get_mof(self):
        if self._mof is None:
            if self.cif_content is not None:
                self._mof = CifReader.read_string(self.cif_content, self.filename)
            else:
                return None
        return self._mof
