import os
import sys

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError, 'SOM_ROOT undefined'

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'lib'))
    
# now import the factories that we may need

from wrappers.ccp4.ccp4_factory import ccp4_factory

class interrogate_pdb:

    def __init__(self):
        self._working_directory = os.getcwd()
        self._ccp4_factory = ccp4_factory()

        self._xyzin = None

        # return results

        self._cell = None
        self._symmetry = None

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        self._ccp4_factory.set_working_directory(working_directory)
        return

    def get_working_directory(self):
        return self._working_directory

    def set_xyzin(self, xyzin):
        self._xyzin = xyzin
        return

    def ccp4(self):
        return self._ccp4_factory

    def interrogate_pdb(self):
        if not self._xyzin:
            raise RuntimeError, 'xyzin not defined'

        for record in open(self._xyzin):
            if 'CRYST1' in record[:6]:
                cell = map(float, record[6:54].split())
                symmetry = record[55:66].strip().replace(' ', '')
                break

        if not cell or not symmetry:
            raise RuntimeError, 'CRYST1 record not found in %s' % self._xyzin

        self._cell = tuple(cell)
        self._symmetry = symmetry

        return

    def get_cell(self):
        return self._cell

    def get_symmetry(self):
        return self._symmetry

if __name__ == '__main__':
    ip = interrogate_pdb()
    ip.set_xyzin(sys.argv[1])
    ip.interrogate_pdb()
    print '%6.3f %6.3f %6.3f %6.3f %6.3f %6.3f' % ip.get_cell()
    print ip.get_symmetry()
