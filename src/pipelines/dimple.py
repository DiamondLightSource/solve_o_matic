# difference_map pipeline customised to work at Diamond...

import os
import sys
import math
import time

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'src'))

# import the modules that we will need

from modules.module_factory import module_factory

# static variables for different modes - think C/C++ #defines

LP_MODE_MR = 'molecular replacement'
LP_MODE_MS = 'molecular substitution'

LP_MODES = [LP_MODE_MR, LP_MODE_MS]

def get_debug():
    if not 'SOM_DEBUG' in os.environ:
        return False

    if int(os.environ['SOM_DEBUG']) == 1:
        return True

    return False

class ligand_pipeline:

    def __init__(self):

        self._working_directory = os.getcwd()
        self._factory = module_factory()

        self._hklin = None
        self._hklout = None
        self._xyzin = None
        self._xyzout = None

        self._nres = None

        self._symmetry = None
        self._reindex_op = None

        self._mode = LP_MODE_MS

        return

    def set_mode(self, mode):
        assert(mode in LP_MODES)
        self._mode = mode
        return

    def set_mode_molecular_replacement(self):
        self._mode = LP_MODE_MR
        return

    def set_mode_molecular_substitution(self):
        self._mode = LP_MODE_MS
        return

    def get_mode(self):
        return self._mode

    def get_modes(self):
        return LP_MODES

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

    def set_xyzout(self, xyzout):
        self._xyzout = xyzout
        return

    def set_symmetry(self, symmetry):
        self._symmetry = symmetry
        return

    def set_reindex_op(self, reindex_op):
        self._reindex_op = reindex_op
        return

    def module(self):
        return self._factory

    def ligand_pipeline(self):
        if self._mode == LP_MODE_MS:
            return self.ligand_pipeline_molecular_substitution()
        if self._mode == LP_MODE_MR:
            return self.ligand_pipeline_molecular_replacement()

        raise RuntimeError('unhandled mode: %s' % self._mode)

    def ligand_pipeline_molecular_substitution(self):

        # this will run the following pipeline:
        #
        # get the cell constants -> prepare the intensity data ->
        # prepare the pdb file -> rigid body refinement -> real refinement

        temporary_files = []

        if not self._hklin:
            raise RuntimeError('hklin not defined')

        if not self._hklout:
            raise RuntimeError('hklout not defined')

        if not self._xyzin:
            raise RuntimeError('xyzin not defined')

        if not self._xyzout:
            raise RuntimeError('xyzout not defined')

        if not self._symmetry:
            # copy the symmetry from the input pdb, if no reindex operation
            # set...

            if self._reindex_op and False:
                raise RuntimeError('symmetry not defined')

            ip = self.module().interrogate_pdb()
            ip.set_xyzin(self._xyzin)
            ip.interrogate_pdb()
            self._symmetry = ip.get_symmetry()

        # prepare intensity data

        name = os.path.split(self._hklin)[-1][:-4]
        hklout = os.path.join(self.get_working_directory(),
                              '%s_idp.mtz' % name)
        temporary_files.append(hklout)

        t0 = time.time()

        idp = self.module().intensity_data_preparation()
        idp.set_hklin(self._hklin)
        idp.set_hklout(hklout)
        idp.set_symmetry(self._symmetry)
        idp.set_xyzin(self._xyzin)
        if self._reindex_op:
            idp.set_reindex_op(self._reindex_op)
        idp.prepare_data_native()

        hklin = hklout

        # prepare the pdb file - N.B. this should include removing the
        # residues which are not in the monomer library

        im = self.module().interrogate_mtz()
        im.set_hklin(hklin)
        im.interrogate_mtz()
        cell = im.get_cell()

        # verify that the resulting unit cell corresponds (roughly)
        # to the CRYST1 record: allow 10% - note well that this has to
        # follow the data preparation

        ip = self.module().interrogate_pdb()
        ip.set_xyzin(self._xyzin)
        ip.interrogate_pdb()
        pdb_cell = ip.get_cell()
        pdb_symmetry = ip.get_symmetry()

        for j in range(6):
            if (math.fabs(pdb_cell[j] - cell[j]) / cell[j]) > 0.1:
                for temporary_file in temporary_files:
                    os.remove(temporary_file)
                raise RuntimeError('mismatching unit cell constants')

        if pdb_symmetry != self._symmetry.replace(' ', ''):
            for temporary_file in temporary_files:
                os.remove(temporary_file)
            raise RuntimeError('mismatching symmetry')

        # copy the experimental cell constants in to the pdb file -> this
        # should give better refinement results

        xyzout = os.path.join(self.get_working_directory(),
                              '%s_pp.pdb' % name)
        temporary_files.append(xyzout)

        pp = self.module().pdb_preparation()
        pp.set_xyzin(self._xyzin)
        pp.set_xyzout(xyzout)
        pp.set_symmetry(self._symmetry)
        pp.set_cell(cell)
        pp.prepare_pdb_refine()

        if get_debug():
            print('Preparation: %.2f' % (time.time() - t0))

        t0 = time.time()

        # run the rb refinement

        xyzin = xyzout
        xyzout = os.path.join(self.get_working_directory(),
                              '%s_rb.pdb' % name)

        temporary_files.append(xyzout)

        rbr = self.module().rigid_body_refine()
        rbr.set_hklin(hklin)
        rbr.set_xyzin(xyzin)
        rbr.set_xyzout(xyzout)
        rbr.rigid_body_refine()

        if get_debug():
            print('Ridig body: %.2f' % (time.time() - t0))

        t0 = time.time()

        # then the "proper" refinement

        xyzin = xyzout

        r = self.module().refine()
        r.set_hklin(hklin)
        r.set_hklout(self._hklout)
        r.set_xyzin(xyzin)
        r.set_xyzout(self._xyzout)
        r.refine()

        if get_debug():
            print('Restrained refinement: %.2f' % (time.time() - t0))

        t0 = time.time()

        # and print out the residuals

        residuals = r.get_residuals()

        print('%5s %6s %6s %6s' % ('Cycle', 'Rwork', 'Rfree', 'FOM'))
        for cycle in sorted(residuals):
            r, rfree, fom = residuals[cycle]
            print('%5d %6.4f %6.4f %6.4f' % (cycle, r, rfree, fom))

        for temporary_file in temporary_files:
            os.remove(temporary_file)

        return

    def ligand_pipeline_molecular_replacement(self):

        # this will run the following pipeline:
        #
        # get the cell constants -> prepare the intensity data ->
        # prepare the pdb file -> rigid body refinement -> real refinement

        temporary_files = []

        if not self._hklin:
            raise RuntimeError('hklin not defined')

        if not self._hklout:
            raise RuntimeError('hklout not defined')

        if not self._xyzin:
            raise RuntimeError('xyzin not defined')

        if not self._xyzout:
            raise RuntimeError('xyzout not defined')

        if not self._symmetry:
            # copy the symmetry from the input pdb, if no reindex operation
            # set...

            if self._reindex_op and False:
                raise RuntimeError('symmetry not defined')

            ip = self.module().interrogate_pdb()
            ip.set_xyzin(self._xyzin)
            ip.interrogate_pdb()
            self._symmetry = ip.get_symmetry()

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

        # prepare the pdb file

        im = self.module().interrogate_mtz()
        im.set_hklin(hklin)
        im.interrogate_mtz()
        cell = im.get_cell()

        # verify that the resulting unit cell corresponds (roughly)
        # to the CRYST1 record: allow 10% - note well that this has to
        # follow the data preparation

        ip = self.module().interrogate_pdb()
        ip.set_xyzin(self._xyzin)
        ip.interrogate_pdb()
        pdb_cell = ip.get_cell()
        pdb_symmetry = ip.get_symmetry()

        for j in range(6):
            if (math.fabs(pdb_cell[j] - cell[j]) / cell[j]) > 0.1:
                for temporary_file in temporary_files:
                    os.remove(temporary_file)
                raise RuntimeError('mismatching unit cell constants')

        if pdb_symmetry != self._symmetry.replace(' ', ''):
            for temporary_file in temporary_files:
                os.remove(temporary_file)
            raise RuntimeError('mismatching symmetry')

        # copy the experimental cell constants in to the pdb file -> this
        # should give better refinement results

        xyzout = os.path.join(self.get_working_directory(),
                              '%s_pp.pdb' % name)
        temporary_files.append(xyzout)

        pp = self.module().pdb_preparation()
        pp.set_xyzin(self._xyzin)
        pp.set_xyzout(xyzout)
        pp.set_symmetry(self._symmetry)
        pp.set_cell(cell)
        pp.prepare_pdb_refine()

        # run some molecular replacement

        xyzin = xyzout
        xyzout = os.path.join(self.get_working_directory(),
                              '%s_rb.pdb' % name)

        hklout = os.path.join(self.get_working_directory(),
                              '%s_rb.mtz' % name)

        temporary_files.append(xyzout)

        mr = self.module().molecular_replace()
        mr.set_hklin(hklin)
        mr.set_hklout(hklout)
        mr.set_xyzin(xyzin)
        mr.set_xyzout(xyzout)
        mr.molecular_replace()

        # then the "proper" refinement

        xyzin = xyzout

        r = self.module().refine()
        r.set_hklin(hklin)
        r.set_hklout(self._hklout)
        r.set_xyzin(xyzin)
        r.set_xyzout(self._xyzout)
        r.refine()

        # and print out the residuals

        residuals = r.get_residuals()

        print('%5s %6s %6s %6s' % ('Cycle', 'Rwork', 'Rfree', 'FOM'))
        for cycle in sorted(residuals):
            r, rfree, fom = residuals[cycle]
            print('%5d %6.4f %6.4f %6.4f' % (cycle, r, rfree, fom))

        for temporary_file in temporary_files:
            os.remove(temporary_file)

        return

# function to guess the point group

def ersatz_pointgroup(spacegroup):

    if not ' ' in spacegroup:
        return spacegroup

    result = ''

    for token in spacegroup.split():
        result += token[0]

    return result

# add a function in here to select the right PDB file - defined as having
# something in common name-wise and having the same pointgroup

def select_right_pdb(hklin, pdb_list):
    '''Find a coordinate file which appears to have the right symmetry.'''

    candidates = []

    im = module_factory().interrogate_mtz()
    im.set_hklin(hklin)
    im.interrogate_mtz()
    reference = ersatz_pointgroup(im.get_symmetry())

    reference_cell = im.get_cell()

    cells = { }

    for xyzin in pdb_list:
        ip = module_factory().interrogate_pdb()
        ip.set_xyzin(xyzin)
        ip.interrogate_pdb()
        if reference == ersatz_pointgroup(ip.get_symmetry_full()):
            candidates.append(xyzin)
            cells[xyzin] = ip.get_cell()

    if len(candidates) == 0:
        raise RuntimeError('no matching coordinate files found')

    # then if there are more than one, see if one matches closer than
    # the others... do this by sorting on the absolute differences in
    # cell constants then picking the closest match

    if len(candidates) == 1:
        return candidates[0]

    diffs = []

    for xyzin in candidates:
        diff = sum([math.fabs(reference_cell[j] - cells[xyzin][j]) \
                    for j in range(6)])
        diffs.append((diff, xyzin))

    diffs.sort()

    return diffs[0][1]

# then add a function to determine (if possible) the right reindexing
# operation for orthorhombic spacegroups

def test_orthorhombic(ref_cell, test_cell):
    '''Test for alternative indexing possibilities for an orthorhombic
    primitive lattice, to handle e.g. P21221 vs. P21212.'''

    for j in 3, 4, 5:
        if int(round(ref_cell[j])) != 90:
            return None

    for j in 3, 4, 5:
        assert(int(round(test_cell[j])) == 90)

    a, b, c = tuple(test_cell[:3])

    best = a * a + b * b + c * c
    best_rdx = None

    # try permuting the cell axes

    for test, reindex in ((a, b, c), 'h,k,l'), \
            ((b, c, a), 'k,l,h'), \
            ((c, a, b), 'l,h,k'):

        diff = sum(
            [(test[j] - ref_cell[j]) * (test[j] - ref_cell[j]) \
             for j in range(3)])

        if diff < best:
            best = diff
            best_rdx = reindex

    assert(best_rdx)

    return best_rdx

# then add a function which will run pointless

if __name__ == '__main__':

    xyzin = None

    candidates = []

    # SCI-857: should be more relaxed here and perhaps ignore the naming
    # filter if there are no names matching?

    for arg in sys.argv[1:]:
        if os.path.split(arg)[-1].split('.')[0].lower() in os.getcwd().lower():
            candidates.append(arg)

    # no matching names, proceed with all files...

    if len(candidates) == 0:
        print('none of the file names matched %s: trying all' % os.getcwd())
        candidates = sys.argv[1:]

    if len(candidates) == 0:
        raise RuntimeError('no candidate pdb files matched %s' % os.getcwd())

    hklin = 'fast_dp.mtz'
    hklout = 'map.mtz'
    xyzout = 'refined.pdb'

    xyzin = select_right_pdb(hklin, candidates)

    if not xyzin:
        raise RuntimeError('no candidate pdb files matched %s' % os.getcwd())

    print('Selected %s' % xyzin)

    im = module_factory().interrogate_mtz()
    im.set_hklin(hklin)
    im.interrogate_mtz()

    reindex_op = None

    if ersatz_pointgroup(im.get_symmetry()) == 'P222':

        # compare unit cells...

        ip = module_factory().interrogate_pdb()
        ip.set_xyzin(xyzin)
        ip.interrogate_pdb()
        reindex_op = test_orthorhombic(ip.get_cell(), im.get_cell())

    lp = ligand_pipeline()
    lp.set_hklin(hklin)
    lp.set_hklout(hklout)
    lp.set_xyzin(xyzin)
    lp.set_xyzout(xyzout)

    if reindex_op:
        lp.set_reindex_op(reindex_op)

    lp.ligand_pipeline()
