import os
import sys
import shutil

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory
from Decorators.DecoratorFactory import DecoratorFactory

def Pointless(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)
    CCP4DriverInstance = DecoratorFactory.Decorate(DriverInstance, 'ccp4')

    class PointlessWrapper(CCP4DriverInstance.__class__):

        def __init__(self):
            CCP4DriverInstance.__class__.__init__(self)
            self.set_executable('pointless')

            self._cc = 0.0
            self._reindex = None

            return

        def check_origin(self):
            self.check_hklin()
            self.check_xyzin()
            self.check_hklout()

            self.start()

            self.close_wait()
            self.check_for_errors()
            self.check_ccp4_errors()

            # get the reindexing operation which was applied... assert that
            # this was the one with the highest correlation coefficient
            # which I think is written out first

            collect = False

            for record in self.get_all_output():

                if 'No possible alternative indexing' in record:
                    self._cc = 1.0
                    self._reindex = 'h,k,l'
                    return self.get_hklin()

                if 'Alternative reindexing' in record and 'CC' in record:
                    collect = True
                    continue

                if collect:
                    self._reindex = record.split()[0][1:-1]
                    self._cc = float(record.split()[1])
                    collect = False

            return self.get_hklout()

        def get_cc(self):
            return self._cc

        def get_reindex(self):
            return self._reindex

    return PointlessWrapper()

if __name__ == '__main__':

    if len(sys.argv) != 4:
        raise RuntimeError('%s hklin xyzin hklout' % sys.argv[0])

    hklin = sys.argv[1]
    xyzin = sys.argv[2]
    hklout = sys.argv[3]

    p = Pointless()

    p.set_hklin(hklin)
    p.set_xyzin(xyzin)
    p.set_hklout(hklout)

    p.check_origin()

    print('%s %.2f' % (p.get_reindex(), p.get_cc()))
