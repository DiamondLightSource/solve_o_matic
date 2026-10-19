import os
import sys

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'lib'))

# now import the factories that we will need

from wrappers.ccp4.ccp4_factory import ccp4_factory

class interrogate_mtz:

    def __init__(self):
        self._working_directory = os.getcwd()
        self._ccp4_factory = ccp4_factory()

        self._hklin = None

        # return results

        self._cell = None
        self._symmetry = None

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        self._ccp4_factory.set_working_directory(working_directory)
        return

    def get_working_directory(self):
        return self._working_directory

    def set_hklin(self, hklin):
        self._hklin = hklin
        return

    def ccp4(self):
        return self._ccp4_factory

    def interrogate_mtz(self):
        if not self._hklin:
            raise RuntimeError('hklin not defined')

        mtzdump = self.ccp4().mtzdump()
        mtzdump.set_hklin(self._hklin)
        mtzdump.mtzdump()

        datasets = mtzdump.get_datasets()

        if len(datasets) != 1:
            raise RuntimeError('need exactly one data set in %s' % \
                  self._hklin)

        info = mtzdump.get_dataset_info(datasets[0])
        self._cell = tuple(info['cell'])
        self._symmetry = info['symmetry']

        return

    def get_cell(self):
        return self._cell

    def get_symmetry(self):
        return self._symmetry

if __name__ == '__main__':
    im = interrogate_mtz()
    im.set_hklin(os.path.join(os.environ['SOM_ROOT'], 'data', 'insulin.mtz'))
    im.interrogate_mtz()
    print(im.get_symmetry())
