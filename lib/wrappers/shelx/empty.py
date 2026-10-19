import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory

def Empty(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)

    class EmptyWrapper(DriverInstance.__class__):
        '''A wrapper class for Empty.'''

        def __init__(self):
            DriverInstance.__class__.__init__(self)

            self.set_executable('empty')

    return EmptyWrapper()
