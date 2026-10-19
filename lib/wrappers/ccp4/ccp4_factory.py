import os

from .cad import Cad
from .freerflag import Freerflag
from .mtzdump import Mtzdump
from .pdbset import Pdbset
from .refmac5 import Refmac5
from .reindex import Reindex
from .truncate import Truncate
from .unique import Unique
from .phaser import Phaser
from .pointless import Pointless

class ccp4_factory:

    def __init__(self):
        self._working_directory = os.getcwd()
        return

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        return

    def cad(self):
        _cad = Cad()
        _cad.set_working_directory(self._working_directory)
        return _cad

    def freerflag(self):
        _freerflag = Freerflag()
        _freerflag.set_working_directory(self._working_directory)
        return _freerflag

    def mtzdump(self):
        _mtzdump = Mtzdump()
        _mtzdump.set_working_directory(self._working_directory)
        return _mtzdump

    def pdbset(self):
        _pdbset = Pdbset()
        _pdbset.set_working_directory(self._working_directory)
        return _pdbset

    def refmac5(self):
        _refmac5 = Refmac5()
        _refmac5.set_working_directory(self._working_directory)
        return _refmac5

    def reindex(self):
        _reindex = Reindex()
        _reindex.set_working_directory(self._working_directory)
        return _reindex

    def truncate(self):
        _truncate = Truncate()
        _truncate.set_working_directory(self._working_directory)
        return _truncate

    def unique(self):
        _unique = Unique()
        _unique.set_working_directory(self._working_directory)
        return _unique

    def phaser(self):
        _phaser = Phaser()
        _phaser.set_working_directory(self._working_directory)
        return _phaser

    def pointless(self):
        _pointless = Pointless()
        _pointless.set_working_directory(self._working_directory)
        return _pointless
