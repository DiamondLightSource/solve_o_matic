import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory
from Decorators.DecoratorFactory import DecoratorFactory

def Freerflag(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)
    CCP4DriverInstance = DecoratorFactory.Decorate(DriverInstance, 'ccp4')

    class FreerflagWrapper(CCP4DriverInstance.__class__):

        def __init__(self):
            # generic things
            CCP4DriverInstance.__class__.__init__(self)
            self.set_executable('freerflag')

            return

        def freerflag(self):
            self.check_hklin()
            self.check_hklout()

            self.start()
            self.close_wait()
            self.check_for_errors()
            self.check_ccp4_errors()

            return

    return FreerflagWrapper()

if __name__ == '__main__':
    # add a free flag to a file which did not have one, confirm that it
    # is now there...

    pass
