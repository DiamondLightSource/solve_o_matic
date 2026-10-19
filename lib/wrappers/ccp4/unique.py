import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory
from Decorators.DecoratorFactory import DecoratorFactory

def Unique(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)
    CCP4DriverInstance = DecoratorFactory.Decorate(DriverInstance, 'ccp4')

    class UniqueWrapper(CCP4DriverInstance.__class__):

        def __init__(self):
            # generic things
            CCP4DriverInstance.__class__.__init__(self)
            self.set_executable('unique')

            # local things
            self._cell = None
            self._symmetry = None
            self._resolution = None

            return

        def set_cell(self, cell):
            self._cell = cell
            return

        def set_symmetry(self, symmetry):
            self._symmetry = symmetry
            return

        def set_resolution(self, resolution):
            self._resolution = resolution
            return

        def unique(self):
            self.check_hklout()

            if not self._cell:
                raise RuntimeError('cell not assigned')

            if not self._symmetry:
                raise RuntimeError('symmetry not assigned')

            if not self._resolution:
                raise RuntimeError('resolution not assigned')

            self.start()
            self.input('cell %f %f %f %f %f %f' % self._cell)
            self.input('symmetry "%s"' % self._symmetry)
            self.input('resolution %f' % self._resolution)
            self.input('labout F=F_UNIQUE SIGF=SIGF_UNIQUE')
            self.close_wait()

            self.check_for_errors()
            self.check_ccp4_errors()

            return

    return UniqueWrapper()

if __name__ == '__main__':

    import tempfile

    hklout = os.path.join(tempfile.mkdtemp(), 'unique-test.mtz')

    unique = Unique()

    unique.set_cell((78.0500, 78.0500, 36.9500,
                     90.0000, 90.0000, 90.0000))
    unique.set_symmetry('P43212')
    unique.set_resolution(1.7)
    unique.set_hklout(hklout)
    unique.unique()

    # should check the properties here...

    os.remove(hklout)
    os.rmdir(os.path.split(hklout)[0])
