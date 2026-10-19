import os
import sys

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'lib'))

# now import the factories that we will need

from wrappers.ccp4.ccp4_factory import ccp4_factory

# first pass this module will just define the methods necessary to prepare
# pdb file for rigid body refinement

class pdb_preparation:

    def __init__(self):

        # this is pretty straight forward - need to essentially define
        # where we're going to work, the input files, the correct
        # spacegroup and optionally the reindex operator

        self._working_directory = os.getcwd()
        self._ccp4_factory = ccp4_factory()

        self._xyzin = None
        self._xyzout = None

        self._symmetry = None
        self._cell = None

        return

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        self._ccp4_factory.set_working_directory(working_directory)
        return

    def get_working_directory(self):
        return self._working_directory

    def set_xyzin(self, xyzin):
        self._xyzin = xyzin
        return

    def set_xyzout(self, xyzout):
        self._xyzout = xyzout
        return

    def set_symmetry(self, symmetry):
        self._symmetry = symmetry
        return

    def set_cell(self, cell):
        self._cell = cell
        return

    # fixme add method to compose list of known monomers from $CLIBD/monomers

    # fixme add method to remove unknown monomers from pdb file

    # accessor methods for the factories

    def ccp4(self):
        return self._ccp4_factory

    # ok, time for a real method now - this will prepare the pdb file for
    # rigid body refinement

    def prepare_pdb_refine(self):
        if not self._xyzin:
            raise RuntimeError('xyzin not defined')

        if not self._xyzout:
            raise RuntimeError('xyzout not defined')

        if not self._symmetry:
            raise RuntimeError('symmetry not defined')

        if not self._cell:
            raise RuntimeError('cell not defined')

        # this will implement the following procedure
        #
        # pdbset

        pdbset = self.ccp4().pdbset()
        pdbset.set_xyzin(self._xyzin)
        pdbset.set_xyzout(self._xyzout)
        pdbset.set_symmetry(self._symmetry)
        pdbset.set_cell(self._cell)
        pdbset.pdbset()

        return

if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise RuntimeError('%s xyzin xyzout hklin' % sys.argv[0])

    xyzin = sys.argv[1]
    xyzout = sys.argv[2]
    hklin = sys.argv[3]

    # get the cell and symmetry from the hklin file

    mtzdump = ccp4_factory().mtzdump()
    mtzdump.set_hklin(hklin)
    mtzdump.mtzdump()

    datasets = mtzdump.get_datasets()

    if len(datasets) != 1:
        raise RuntimeError('need exactly one data set in %s' % \
              self._hklin)

    info = mtzdump.get_dataset_info(datasets[0])
    cell = tuple(info['cell'])
    symmetry = info['symmetry']

    pp = pdb_preparation()
    pp.set_xyzin(xyzin)
    pp.set_xyzout(xyzout)
    pp.set_symmetry(symmetry)
    pp.set_cell(cell)

    pp.prepare_pdb_refine()
