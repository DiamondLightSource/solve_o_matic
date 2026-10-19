import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory
from Decorators.DecoratorFactory import DecoratorFactory

def Reindex(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)
    CCP4DriverInstance = DecoratorFactory.Decorate(DriverInstance, 'ccp4')

    class ReindexWrapper(CCP4DriverInstance.__class__):

        def __init__(self):
            # generic things
            CCP4DriverInstance.__class__.__init__(self)
            self.set_executable('reindex')

            # reindex specific things
            self._symmetry = None
            self._reindex_op = None

            return

        def set_symmetry(self, symmetry):
            self._symmetry = symmetry
            return

        def set_reindex_op(self, reindex_op):
            self._reindex_op = reindex_op
            return

        def reindex(self):
            self.check_hklin()
            self.check_hklout()

            if not self._symmetry and not self._reindex_op:
                raise RuntimeError('assign either spacegroup or reindex')

            self.start()

            if self._symmetry:
                self.input('symmetry %s' % self._symmetry)
            if self._reindex_op:
                self.input('reindex %s' % self._reindex_op)

            self.close_wait()

            self.check_for_errors()
            self.check_ccp4_errors()

            return

    return ReindexWrapper()

if __name__ == '__main__':
    # in here add a test which will run reindex, then mtzdump to ensure
    # that the reindexing was successful.
    pass
