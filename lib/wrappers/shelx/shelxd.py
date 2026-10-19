import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory

def Shelxd(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)

    class ShelxdWrapper(DriverInstance.__class__):

        def __init__(self):
            DriverInstance.__class__.__init__(self)

            self.set_executable('shelxd')

            self._name = None
            self._cc = None
            self._cc_weak = None
            return

        def set_name(self, name):
            self._name = name

            return

        def shelxd(self):
            if not self._name:
                raise RuntimeError('name not assigned')

            # check that the input files are present according to self._name

            self.add_command_line('%s_fa' % self._name)

            self.start()
            self.close_wait()

            # FIXME get the final CC weak from the output

            for record in self.get_all_output():
                if 'All/Weak' in record:
                    tokens = record.split()
                    self._cc = float(tokens[8])
                    self._cc_weak = float(tokens[10].replace(',', ''))

            return

        def get_cc(self):
            return self._cc, self._cc_weak


    return ShelxdWrapper()

if __name__ == '__main__':
    # FIXME add test
    pass
