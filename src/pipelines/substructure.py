import os
import sys

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'src'))

# import the modules that we will need

from modules.module_factory import module_factory

class shelx_cc_weak_pipeline:

    def __init__(self):

        self._working_directory = os.getcwd()
        self._factory = module_factory()

        self._hklin = None
        self._nha = None

        self._symmetry = None
        self._reindex_op = None

        self._cc = None
        self._cc_weak = None

        return

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        self._factory.set_working_directory(working_directory)
        return

    def get_working_directory(self):
        return self._working_directory

    def set_hklin(self, hklin):
        self._hklin = hklin
        return

    def set_nha(self, nha):
        self._nha = nha
        return

    def set_symmetry(self, symmetry):
        self._symmetry = symmetry
        return

    def set_reindex_op(self, reindex_op):
        self._reindex_op = reindex_op
        return

    def module(self):
        return self._factory

    def get_cc(self):
        return self._cc, self._cc_weak

    def shelx_cc_weak_pipeline(self):

        # this will run the following pipeline:
        #
        # get the cell constants -> prepare the intensity data ->
        # prepare the pdb file -> rigid body refinement -> real refinement

        temporary_files = []

        if not self._hklin:
            raise RuntimeError('hklin not defined')

        if not self._nha:
            raise RuntimeError('nha not defined')

        if not self._symmetry:
            raise RuntimeError('symmetry not defined')

        # prepare intensity data

        name = os.path.split(self._hklin)[-1][:-4]
        hklout = os.path.join(self.get_working_directory(),
                              '%s_idp.mtz' % name)
        temporary_files.append(hklout)

        idp = self.module().intensity_data_preparation()
        idp.set_hklin(self._hklin)
        idp.set_hklout(hklout)
        idp.set_symmetry(self._symmetry)
        if self._reindex_op:
            idp.set_reindex_op(self._reindex_op)
        idp.prepare_data_native()

        hklin = hklout

        fs = self.module().find_sites()
        fs.set_hklin(hklin)
        fs.set_nha(self._nha)
        fs.find_sites()

        self._cc, self._cc_weak = fs.get_cc()

        for temporary_file in temporary_files:
            os.remove(temporary_file)

        return

if __name__ == '__main__':

    if len(sys.argv) < 4 or len(sys.argv) > 5:
        raise RuntimeError('%s hklin nha symm [reindex_op]' % sys.argv[0])

    hklin = sys.argv[1]
    nha = int(sys.argv[2])
    symmetry = sys.argv[3]
    if len(sys.argv) == 5:
        reindex_op = sys.argv[4]
    else:
        reindex_op = None

    scwp = shelx_cc_weak_pipeline()
    scwp.set_hklin(hklin)
    scwp.set_nha(nha)
    scwp.set_symmetry(symmetry)
    if reindex_op:
        scwp.set_reindex_op(reindex_op)

    scwp.shelx_cc_weak_pipeline()
