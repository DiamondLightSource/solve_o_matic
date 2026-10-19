import os
import sys

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'lib'))

# now import the factories that we will need

from wrappers.ccp4.ccp4_factory import ccp4_factory

# first pass this module will just provide a wrapper for the restrained
# refinement in refmac5...

class refine:

    def __init__(self):
        self._working_directory = os.getcwd()
        self._ccp4_factory = ccp4_factory()

        self._hklin = None
        self._hklout = None

        self._xyzin = None
        self._xyzout = None

        # return values

        self._residuals = { }

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

    def ccp4(self):
        return self._ccp4_factory

    def refine(self):
        if not self._hklin:
            raise RuntimeError('hklin not defined')

        if not self._hklout:
            raise RuntimeError('hklout not defined')

        if not self._xyzin:
            raise RuntimeError('xyzin not defined')

        if not self._xyzout:
            raise RuntimeError('xyzout not defined')

        refmac5 = self.ccp4().refmac5()

        refmac5.set_hklin(self._hklin)
        refmac5.set_hklout(self._hklout)
        refmac5.set_xyzin(self._xyzin)
        refmac5.set_xyzout(self._xyzout)

        refmac5.set_mode_restrained()
        refmac5.set_ncycles(7)
        refmac5.refmac5()

        fout = open('refmac_restrained.log', 'w')

        for record in refmac5.get_all_output():
            fout.write(record)

        fout.close()

        # fixme - check the status

        # get the loggraphs out

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

            self._residuals[cycle] = (r, rfree, fom)

        return

    def get_residuals(self):
        return self._residuals

if __name__ == '__main__':
    # then I should run a test...
    pass
