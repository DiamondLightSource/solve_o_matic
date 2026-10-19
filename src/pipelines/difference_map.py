import os
import sys
import math

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'src'))

# import the modules that we will need

from modules.module_factory import module_factory

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

            if self._reindex_op:
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

if __name__ == '__main__':

    if len(sys.argv) < 5 or len(sys.argv) > 7:
        raise RuntimeError('%s hklin xyzin hklout xyzout [symm] [reindex_op]' % sys.argv[0])

    hklin = sys.argv[1]
    xyzin = sys.argv[2]
    hklout = sys.argv[3]
    xyzout = sys.argv[4]

    if len(sys.argv) > 5:
        symmetry = sys.argv[5]
    else:
        symmetry = None

    if len(sys.argv) > 6:
        reindex_op = sys.argv[6]
    else:
        reindex_op = None

    lp = ligand_pipeline()
    lp.set_hklin(hklin)
    lp.set_hklout(hklout)
    lp.set_xyzin(xyzin)
    lp.set_xyzout(xyzout)

    if symmetry:
        lp.set_symmetry(symmetry)
    if reindex_op:
        lp.set_reindex_op(reindex_op)

    lp.ligand_pipeline()
