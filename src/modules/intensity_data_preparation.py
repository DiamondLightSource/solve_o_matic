import os
import sys

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'lib'))

# external modules used here

from .interrogate_mtz import interrogate_mtz
from .symmetry_information import symmetry_information

# now import the factories that we will need

from wrappers.ccp4.ccp4_factory import ccp4_factory

# first pass this module will just define the methods necessary to prepare
# data for rigid body refinement & molecular replacement

class intensity_data_preparation:

    def __init__(self):

        # this is pretty straight forward - need to essentially define
        # where we're going to work, the input files, the correct
        # spacegroup and optionally the reindex operator

        self._working_directory = os.getcwd()
        self._ccp4_factory = ccp4_factory()

        self._hklin = None
        self._hklout = None
        self._xyzin = None

        self._nres = None

        self._symmetry = None
        self._reindex_op = None

        self._symmetry_information = symmetry_information()

        return

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        self._ccp4_factory.set_working_directory(working_directory)
        return

    def get_working_directory(self):
        return self._working_directory

    def set_hklin(self, hklin):
        self._hklin = hklin
        return

    def set_hklout(self, hklout):
        self._hklout = hklout
        return

    def set_xyzin(self, xyzin):
        self._xyzin = xyzin
        return

    def set_nres(self, nres):
        self._nres = nres
        return

    def set_symmetry(self, symmetry):

        # verify that this symmetry is recognised

        pointgroup = self._symmetry_information.get_pointgroup(symmetry)

        self._symmetry = symmetry
        return

    def set_reindex_op(self, reindex_op):
        self._reindex_op = reindex_op
        return

    # accessor methods for the factories

    def ccp4(self):
        return self._ccp4_factory

    # ok, time for a "real" method now - this will prepare data for
    # molecular replacement / refinement

    def prepare_data_native(self):

        temporary_files = []

        if not self._hklin:
            raise RuntimeError('hklin not defined')

        if not self._hklout:
            raise RuntimeError('hklout not defined')

        if not self._symmetry:
            raise RuntimeError('symmetry not defined')

        # first check that the crystal pointgroup corresponds to the
        # specified symmetry

        im = interrogate_mtz()
        im.set_working_directory(self._working_directory)
        im.set_hklin(self._hklin)
        im.interrogate_mtz()

        cell = im.get_cell()
        symmetry = im.get_symmetry()

        if self._symmetry_information.get_pointgroup(symmetry) != \
           self._symmetry_information.get_pointgroup(self._symmetry):
            for temporary_file in temporary_files:
                os.remove(temporary_file)
            raise RuntimeError('symmetry mismatch')

        # this will implement the following procedure:
        #
        # reindex -> truncate -> cad
        # unique -> freerflag /

        name = os.path.split(self._hklin)[-1][:-4]

        hklin = self._hklin
        hklout = os.path.join(self.get_working_directory(),
                              '%s_reindex.mtz' % name)

        temporary_files.append(hklout)

        # if we have an input coordinate file, use pointless to compare
        # these measurements, else just reindex according to the input
        # reindexing operation. N.B. may need to run reindex anyways to
        # assign the spacegroup to these measurements.

        if self._xyzin:

            pointless = self.ccp4().pointless()
            pointless.set_hklin(hklin)
            pointless.set_xyzin(self._xyzin)
            pointless.set_hklout(hklout)

            # pointless wrapper will return hklin if no alternative
            # indexing is possible

            hklout = pointless.check_origin()

            if os.path.exists(hklout):
                hklin = hklout
            hklout = os.path.join(self.get_working_directory(),
                                  '%s_reindex_sg.mtz' % name)
            temporary_files.append(hklout)

            reindex = self.ccp4().reindex()
            reindex.set_hklin(hklin)
            reindex.set_hklout(hklout)
            reindex.set_symmetry(self._symmetry)
            reindex.reindex()

        else:

            reindex = self.ccp4().reindex()
            reindex.set_hklin(hklin)
            reindex.set_hklout(hklout)
            reindex.set_symmetry(self._symmetry)
            if self._reindex_op:
                reindex.set_reindex_op(self._reindex_op)
            reindex.reindex()

        hklin = hklout
        hklout = os.path.join(self.get_working_directory(),
                              '%s_truncate.mtz' % name)

        temporary_files.append(hklout)

        truncate = self.ccp4().truncate()
        truncate.set_hklin(hklin)
        truncate.set_hklout(hklout)
        if self._nres:
            truncate.set_nres(self._nres)
        truncate.truncate()

        truncated_data = hklout

        # now generate the unique file full of FreeR_flag values:
        # first need to read symmetry, cell constants and resolution
        # range from the input file

        mtzdump = self.ccp4().mtzdump()
        mtzdump.set_hklin(hklin)
        mtzdump.mtzdump()

        datasets = mtzdump.get_datasets()

        if len(datasets) != 1:
            raise RuntimeError('need exactly one data set in %s' % \
                  self._hklin)

        info = mtzdump.get_dataset_info(datasets[0])
        cell = tuple(info['cell'])
        symmetry = info['symmetry']
        resolution = min(mtzdump.get_resolution_range())

        hklout = os.path.join(self.get_working_directory(),
                              '%s_unique.mtz' % name)
        temporary_files.append(hklout)

        unique = self.ccp4().unique()
        unique.set_hklout(hklout)
        unique.set_symmetry(symmetry)
        unique.set_cell(cell)
        unique.set_resolution(resolution)
        unique.unique()

        hklin = hklout
        hklout = os.path.join(self.get_working_directory(),
                              '%s_free.mtz' % name)
        temporary_files.append(hklout)

        freerflag = self.ccp4().freerflag()
        freerflag.set_hklin(hklin)
        freerflag.set_hklout(hklout)
        freerflag.freerflag()

        free_data = hklout

        cad = self.ccp4().cad()
        cad.add_hklin(truncated_data)
        cad.set_freein(free_data)
        cad.set_hklout(self._hklout)
        cad.copyfree()

        # ok, I think we're all done now... remove the temporary files

        for temporary_file in temporary_files:
            try:
                os.remove(temporary_file)
            except:
                pass

        return

if __name__ == '__main__':

    if len(sys.argv) < 4 or len(sys.argv) > 5:
        raise RuntimeError('%s hklin hklout symmetry [reindex_op]' % \
              sys.argv[0])

    hklin = sys.argv[1]
    hklout = sys.argv[2]
    symmetry = sys.argv[3]
    if len(sys.argv) == 5:
        reindex_op = sys.argv[4]
    else:
        reindex_op = None

    idp = intensity_data_preparation()
    idp.set_hklin(hklin)
    idp.set_hklout(hklout)
    idp.set_symmetry(symmetry)
    if reindex_op:
        idp.set_reindex_op(reindex_op)

    idp.prepare_data_native()
