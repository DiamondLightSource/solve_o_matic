import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

xia2core_root = os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python')

if not xia2core_root in sys.path:
    sys.path.append(xia2core_root)

from Driver.DriverFactory import DriverFactory
from Decorators.DecoratorFactory import DecoratorFactory

def Pdbset(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)
    CCP4DriverInstance = DecoratorFactory.Decorate(DriverInstance, 'ccp4')

    class PdbsetWrapper(CCP4DriverInstance.__class__):

        def __init__(self):
            # generic things
            CCP4DriverInstance.__class__.__init__(self)
            self.set_executable('pdbset')

            # specific things
            self._cell = None
            self._symmetry = None

            return

        def set_cell(self, cell):
            self._cell = cell
            return

        def set_symmetry(self, symmetry):
            self._symmetry = symmetry
            return

        def pdbset(self):
            self.check_xyzin()
            self.check_xyzout()

            if not self._cell:
                raise RuntimeError('cell not assigned')

            if not self._symmetry:
                raise RuntimeError('symmetry not assigned')

            self.start()
            self.input('cell %f %f %f %f %f %f' % self._cell)
            self.input('symmetry "%s"' % self._symmetry)
            self.close_wait()

            self.check_for_errors()
            self.check_ccp4_errors()

            return

    return PdbsetWrapper()

if __name__ == '__main__':
    # FIXME add a test
    pass
