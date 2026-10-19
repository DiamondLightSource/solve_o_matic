import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory

def Shelxc(DriverType = None):
    DriverInstance = DriverFactory.Driver(DriverType)

    class ShelxcWrapper(DriverInstance.__class__):

        def __init__(self):
            DriverInstance.__class__.__init__(self)

            self.set_executable('shelxc')

            # input files
            self._infl = None
            self._lrem = None
            self._peak = None
            self._hrem = None
            self._sad = None
            self._native = None

            # heavy atom information
            self._nha = 0

            # cell and symmetry
            self._cell = None
            self._symmetry = None

            # naming information
            self._name = None

        def set_cell(self, cell):
            self._cell = cell
            return

        def set_symmetry(self, symmetry):
            self._symmetry = symmetry
            return

        def set_nha(self, nha):
            self._nha = nha
            return

        def set_peak(self, peak):
            self._peak = peak
            return

        def set_infl(self, infl):
            self._infl = infl
            return

        def set_lrem(self, lrem):
            self._lrem = lrem
            return

        def set_hrem(self, hrem):
            self._hrem = hrem
            return

        def set_native(self, native):
            self._native = native
            return

        def set_sad(self, sad):
            self._sad = sad
            return

        def set_name(self, name):
            self._name = name
            return

        def check_input(self):

            # check that the input parameters are set sensibly...
            # require at the minimum:
            #
            # SAD
            # - xor -
            # ((PEAK or INFL) and (HREM or LREM))

            pass

        def shelxc(self):

            self.check_input()

            self.add_command_line(self._name)

            self.start()

            if self._peak:
                self.input('PEAK %s\n' % self._peak)
            if self._infl:
                self.input('INFL %s\n' % self._infl)
            if self._hrem:
                self.input('HREM %s\n' % self._hrem)
            if self._lrem:
                self.input('LREM %s\n' % self._lrem)
            if self._sad:
                self.input('SAD %s\n' % self._sad)
            if self._native:
                self.input('NATIVE %s\n' % self._native)

            self.input('CELL %f %f %f %f %f %f' % tuple(self._cell))
            self.input('SPAG %s' % self._symmetry)
            self.input('FIND %d' % self._nha)
            self.input('NTRY 50')
            self.input('MIND -3.5')

            self.close_wait()

            return

    return ShelxcWrapper()

if __name__ == '__main__':
    # FIXME add a test
    pass
