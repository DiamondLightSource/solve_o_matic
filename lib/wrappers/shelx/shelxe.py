import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory

def Shelxe(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)

    class ShelxeWrapper(DriverInstance.__class__):

        def __init__(self):
            DriverInstance.__class__.__init__(self)

            self.set_executable('shelxe')

            self._name = None
            self._solvent = 0.0
            self._enantiomorph = False

        def set_solvent(self, solvent):
            self._solvent = solvent
            return

        def set_name(self, name):
            self._name = name
            return

        def set_enantiomorph(self, enantiomorph = True):
            self._enantiomorph = enantiomorph
            return

        def shelxe(self):

            self.add_command_line('%s' % self._name)
            self.add_command_line('%s_fa' % self._name)
            self.add_command_line('-h')
            self.add_command_line('-s%f' % self._solvent)
            self.add_command_line('-m20')

            if self._enantiomorph:
                self.add_command_line('-i')

            self.start()

            self.close_wait()

            # read the CC's and what-have-you from the lst file

            return

    return ShelxeWrapper()

if __name__ == '__main__':
    # FIXME add a test
    pass
