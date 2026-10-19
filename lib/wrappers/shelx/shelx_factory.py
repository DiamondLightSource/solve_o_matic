import os

from .mtz2sca import Mtz2sca as _Mtz2sca
from .shelxc import Shelxc as _Shelxc
from .shelxd import Shelxd as _Shelxd
from .shelxe import Shelxe as _Shelxe

class shelx_factory:

    def __init__(self):
        self._working_directory = os.getcwd()
        return

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        return

    def mtz2sca(self):
        _mtz2sca = _Mtz2sca()
        _mtz2sca.set_working_directory(self._working_directory)
        return _mtz2sca

    def shelxc(self):
        _shelxc = _Shelxc()
        _shelxc.set_working_directory(self._working_directory)
        return _shelxc

    def shelxd(self):
        _shelxd = _Shelxd()
        _shelxd.set_working_directory(self._working_directory)
        return _shelxd

    def shelxe(self):
        _shelxe = _Shelxe()
        _shelxe.set_working_directory(self._working_directory)
        return _shelxe
