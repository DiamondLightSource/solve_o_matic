import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory

def Mtz2sca(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)

    class Mtz2scaWrapper(DriverInstance.__class__):
        '''A wrapper class for Mtz2sca.'''

        def __init__(self):
            DriverInstance.__class__.__init__(self)

            self.set_executable('mtz2sca')

            self._hklin = None
            self._scaout = None

            return

        def set_hklin(self, hklin):
            self._hklin = hklin
            return

        def set_scaout(self, scaout):
            self._scaout = scaout
            return

        def mtz2sca(self):
            self.add_command_line(self._hklin)
            self.add_command_line(self._scaout)
            self.start()
            self.close_wait()
            self.check_for_errors()

            return

    return Mtz2scaWrapper()

if __name__ == '__main__':
    # FIXME add a test in here
    pass
