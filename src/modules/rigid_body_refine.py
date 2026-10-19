import os
import sys

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'lib'))

# now import the factories that we will need

from wrappers.ccp4.ccp4_factory import ccp4_factory

# and any helpful modules

from .interrogate_pdb import interrogate_pdb

class rigid_body_refine:

    def __init__(self):
        self._working_directory = os.getcwd()
        self._ccp4_factory = ccp4_factory()

        self._hklin = None
        self._hklout = None

        self._xyzin = None
        self._xyzout = None

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

    def set_xyzin(self, xyzin):
        self._xyzin = xyzin
        return

    def set_xyzout(self, xyzout):
        self._xyzout = xyzout
        return

    def ccp4(self):
        return self._ccp4_factory

    def rigid_body_refine(self):
        if not self._hklin:
            raise RuntimeError('hklin not defined')

        if not self._xyzin:
            raise RuntimeError('xyzin not defined')

        if not self._xyzout:
            raise RuntimeError('xyzout not defined')

        name = os.path.split(self._hklin)[-1][:-4]

        hklout = os.path.join(self.get_working_directory(),
                              '%s_refmac5_rb.mtz' % name)

        refmac5 = self.ccp4().refmac5()

        refmac5.set_hklin(self._hklin)
        refmac5.set_hklout(hklout)
        refmac5.set_xyzin(self._xyzin)
        refmac5.set_xyzout(self._xyzout)

        refmac5.set_mode_rigidbody()
        refmac5.refmac5()

        os.remove(hklout)

        fout = open('refmac_rigid_body.log', 'w')

        for record in refmac5.get_all_output():
            fout.write(record)

        fout.close()
        # get r factor - if < 45% return, else run mr

        loggraphs = refmac5.parse_ccp4_loggraph()

        loggraph = loggraphs['Rfactor analysis, stats vs cycle']

        cycle_col = loggraph['columns'].index('Ncyc')
        r_col = loggraph['columns'].index('Rfact')
        rfree_col = loggraph['columns'].index('Rfree')
        fom_col = loggraph['columns'].index('FOM')

        for record in loggraph['data']:
            cycle = int(record[cycle_col])
            r = float(record[r_col])
            rfree = float(record[rfree_col])
            fom = float(record[fom_col])

        if r < 0.45:

            return

        # ok perhaps run some mr...

        print('Rigid body refinement failed: trying MR')

        ip = interrogate_pdb()

        ip.set_xyzin(self._xyzin)
        ip.interrogate_pdb()

        mw = ip.get_molecular_weight()

        phaser = self.ccp4().phaser()

        hklout = os.path.join(self.get_working_directory(),
                              '%s_phaser_mr.mtz' % name)

        phaser.set_hklin(self._hklin)
        phaser.set_hklout(hklout)
        phaser.set_xyzin(self._xyzin)
        phaser.set_xyzout(self._xyzout)
        phaser.set_molecular_weight(mw)

        phaser.mr()

        os.remove(hklout)

        return

if __name__ == '__main__':
    # then I should run a test...
    pass
