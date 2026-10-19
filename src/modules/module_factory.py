import os

from .intensity_data_preparation import intensity_data_preparation as \
     _intensity_data_preparation
from .pdb_preparation import pdb_preparation as _pdb_preparation
from .rigid_body_refine import rigid_body_refine as _rigid_body_refine
from .refine import refine as _refine
from .interrogate_mtz import interrogate_mtz as _interrogate_mtz
from .interrogate_pdb import interrogate_pdb as _interrogate_pdb
from .symmetry_information import symmetry_information as \
     _symmetry_information
from .find_sites import find_sites as _find_sites
from .characterise_diffraction import characterise_diffraction as \
     _characterise_diffraction
from .calculate_strategy import calculate_strategy as \
     _calculate_strategy
from .calculate_better_strategy import calculate_better_strategy as \
     _calculate_better_strategy

class module_factory:

    def __init__(self):
        self._working_directory = os.getcwd()
        return

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        return

    def intensity_data_preparation(self):
        intensity_data_preparation_instance = _intensity_data_preparation()
        intensity_data_preparation_instance.set_working_directory(
            self._working_directory)
        return intensity_data_preparation_instance

    def pdb_preparation(self):
        pdb_preparation_instance = _pdb_preparation()
        pdb_preparation_instance.set_working_directory(
            self._working_directory)
        return pdb_preparation_instance

    def rigid_body_refine(self):
        rigid_body_refine_instance = _rigid_body_refine()
        rigid_body_refine_instance.set_working_directory(
            self._working_directory)
        return rigid_body_refine_instance

    def refine(self):
        refine_instance = _refine()
        refine_instance.set_working_directory(self._working_directory)
        return refine_instance

    def interrogate_mtz(self):
        interrogate_mtz_instance = _interrogate_mtz()
        interrogate_mtz_instance.set_working_directory(self._working_directory)
        return interrogate_mtz_instance

    def interrogate_pdb(self):
        interrogate_pdb_instance = _interrogate_pdb()
        interrogate_pdb_instance.set_working_directory(self._working_directory)
        return interrogate_pdb_instance

    def symmetry_information(self):
        return _symmetry_information()

    def find_sites(self):
        find_sites_instance = _find_sites()
        find_sites_instance.set_working_directory(self._working_directory)
        return find_sites_instance

    def characterise_diffraction(self):
        characterise_diffraction_instance = _characterise_diffraction()
        characterise_diffraction_instance.set_working_directory(
            self._working_directory)
        return characterise_diffraction_instance

    def calculate_strategy(self):
        calculate_strategy_instance = _calculate_strategy()
        calculate_strategy_instance.set_working_directory(
            self._working_directory)
        return calculate_strategy_instance

    def calculate_better_strategy(self):
        calculate_better_strategy_instance = _calculate_better_strategy()
        calculate_better_strategy_instance.set_working_directory(
            self._working_directory)
        return calculate_better_strategy_instance
