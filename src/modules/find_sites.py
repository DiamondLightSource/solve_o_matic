import os
import sys

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'lib'))

# now import the factories that we will need

from wrappers.shelx.shelx_factory import shelx_factory
from wrappers.ccp4.ccp4_factory import ccp4_factory

class find_sites:

    def __init__(self):
        self._working_directory = os.getcwd()
        self._shelx_factory = shelx_factory()
        self._ccp4_factory = ccp4_factory()

        self._hklin = None
        self._name = 'som_sad'
        self._nha = 0

        self._cc = None
        self._cc_weak = None

        return

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        self._ccp4_factory.set_working_directory(working_directory)
        self._shelx_factory.set_working_directory(working_directory)
        return

    def get_working_directory(self):
        return self._working_directory

    def set_hklin(self, hklin):
        self._hklin = hklin
        return

    def set_nha(self, nha):
        self._nha = nha
        return

    def set_name(self, name):
        self._name = name
        return

    def ccp4(self):
        return self._ccp4_factory

    def shelx(self):
        return self._shelx_factory

    def get_cc(self):
        return self._cc, self._cc_weak

    def find_sites(self):

        temporary_files = []

        # first get the cell / symmetry

        mtzdump = self.ccp4().mtzdump()
        mtzdump.set_hklin(self._hklin)
        mtzdump.mtzdump()

        datasets = mtzdump.get_datasets()

        # FIXME need to handle this gracefully - more than one data set
        # is fine though I will need their names, e.g. SAD, PEAK and so on.

        if len(datasets) != 1:
            raise RuntimeError('need exactly one data set in %s' % \
                  self._hklin)

        info = mtzdump.get_dataset_info(datasets[0])
        cell = tuple(info['cell'])
        symmetry = info['symmetry']

        # now run mtz2sca -> get a useful input file

        scaout = os.path.join(self.get_working_directory(),
                              '%s.sca' % os.path.split(self._hklin)[-1][:-4])
        temporary_files.append(scaout)

        mtz2sca = self.shelx().mtz2sca()
        mtz2sca.set_hklin(self._hklin)
        mtz2sca.set_scaout(scaout)
        mtz2sca.mtz2sca()

        # then shelxc -> fa esimates and "native" for downstream
        # N.B. this will produce all sorts of temp files which will
        # need to be tidied up

        shelxc = self.shelx().shelxc()
        shelxc.set_cell(cell)
        shelxc.set_symmetry(symmetry)
        shelxc.set_nha(self._nha)
        shelxc.set_sad(scaout)
        shelxc.set_name(self._name)
        shelxc.shelxc()

        # shelxc makes the following files:
        for f in '_fa.ins', '_fa.hkl', '.hkl':
            temporary_files.append(os.path.join(self.get_working_directory(),
                                                '%s%s' % (self._name, f)))

        # find sites, get the CC stats

        shelxd = self.shelx().shelxd()
        shelxd.set_name(self._name)
        shelxd.shelxd()

        cc, cc_weak = shelxd.get_cc()

        # shelxd makes the following files:
        for f in '_fa.pdb', '_fa.res', '_fa.lst':
            temporary_files.append(os.path.join(self.get_working_directory(),
                                                '%s%s' % (self._name, f)))


        self._cc = cc
        self._cc_weak = cc_weak

        for temporary_file in temporary_files:
            try:
                os.remove(temporary_file)
            except OSError as e:
                pass

        return

if __name__ == '__main__':
    # then run a test!
    pass
