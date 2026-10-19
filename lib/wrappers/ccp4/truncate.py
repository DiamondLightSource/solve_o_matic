import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory
from Decorators.DecoratorFactory import DecoratorFactory

def Truncate(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)
    CCP4DriverInstance = DecoratorFactory.Decorate(DriverInstance, 'ccp4')

    class TruncateWrapper(CCP4DriverInstance.__class__):

        def __init__(self):
            # generic things
            CCP4DriverInstance.__class__.__init__(self)
            self.set_executable('truncate')

            # specific things
            self._nres = None

            return

        def set_nres(self, nres):
            self._nres = nres
            return

        def truncate(self):
            self.check_hklin()
            self.check_hklout()

            self.start()
            if self._nres:
                self.input('nres %d' % self._nres)
            self.close_wait()

            self.check_for_errors()
            self.check_ccp4_errors()

            return

    return TruncateWrapper()

if __name__ == '__main__':
    # write ye a test
    pass
