import os
import sys
import copy

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

xia2core_root = os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python')

if not xia2core_root in sys.path:
    sys.path.append(xia2core_root)

from Driver.DriverFactory import DriverFactory
from Decorators.DecoratorFactory import DecoratorFactory

def Mtzdump(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)
    CCP4DriverInstance = DecoratorFactory.Decorate(DriverInstance, 'ccp4')

    class MtzdumpWrapper(CCP4DriverInstance.__class__):

        def __init__(self):
            # generic things
            CCP4DriverInstance.__class__.__init__(self)
            self.set_executable('mtzdump')

            # return information
            self._header = { }
            self._header['datasets'] = []
            self._header['dataset_info'] = { }

            self._batch_header = { }

            self._batches = None
            self._reflections = 0
            self._resolution_range = (0, 0)

            return

        def mtzdump(self):
            self.check_hklin()

            self.start()
            self.close_wait()

            self.check_for_errors()
            self.check_ccp4_errors()

            # ok, read out the information to the waiting dictionaries

            output = self.get_all_output()

            length = len(output)

            batches = []

            for i in range(length):
                line = output[i][:-1]

                if 'Batch number:' in line:
                    batch = int(output[i + 1].split()[0])
                    if not batch in batches:
                        batches.append(batch)

                if 'Column Labels' in line:
                    # then the column labels are in two lines time...
                    labels = output[i + 2].strip().split()
                    self._header['column_labels'] = labels

                if 'Column Types' in line:
                    # then the column types are in two lines time...
                    types = output[i + 2].strip().split()
                    self._header['column_types'] = types

                if 'Resolution Range' in line:
                    self._resolution_range = tuple(
                        map(float, output[i + 2].replace('-', ' ').split(
                        '(')[1].split()[:2]))

                if 'Space group' in line and '\'' in line:
                    self._header['symmetry'] = line.split('\'')[1].strip()

                if 'Dataset ID, ' in line:
                    block = 0
                    while output[block * 5 + i + 2].strip():
                        dataset_number = int(
                            output[5 * block + i + 2].split()[0])
                        project = output[5 * block + i + 2][10:].strip()
                        crystal = output[5 * block + i + 3][10:].strip()
                        dataset = output[5 * block + i + 4][10:].strip()
                        cell = list(map(float, output[5 * block + i + 5].strip(
                            ).split()))
                        wavelength = float(output[5 * block + i + 6].strip())

                        dataset_id = '%s/%s/%s' % \
                                     (project, crystal, dataset)

                        if not dataset_id in self._header['datasets']:

                            self._header['datasets'].append(dataset_id)
                            self._header['dataset_info'][dataset_id] = { }
                            self._header['dataset_info'][
                                dataset_id]['wavelength'] = wavelength
                            self._header['dataset_info'][
                                dataset_id]['cell'] = cell
                            self._header['dataset_info'][
                                dataset_id]['id'] = dataset_number

                        block += 1

                if 'No. of reflections used in FILE STATISTICS' in line:
                    self._reflections = int(line.split()[-1])

            self._batches = batches

            return

        def get_columns(self):
            results = []
            for i in range(len(self._header['column_labels'])):
                results.append((self._header['column_labels'][i],
                                self._header['column_types'][i]))
            return results

        def get_resolution_range(self):
            return self._resolution_range

        def get_datasets(self):
            return self._header['datasets']

        def get_dataset_info(self, dataset):
            result = copy.deepcopy(self._header['dataset_info'][dataset])
            result['symmetry'] = self._header['symmetry']
            return result

        def get_symmetry(self):
            return self._header['symmetry']

        def get_batches(self):
            return self._batches

    return MtzdumpWrapper()

if __name__ == '__main__':

    mtzdump = Mtzdump()

    mtzdump.set_hklin(sys.argv[1])
    mtzdump.mtzdump()

    columns = mtzdump.get_columns()

    for c in columns:
        print('%12s (%s)' % c)

    datasets = mtzdump.get_datasets()

    for d in datasets:
        print('%s' % d)
        info = mtzdump.get_dataset_info(d)
        print('%s (%6.4fA) %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f' % \
              (info['symmetry'], info['wavelength'],
               info['cell'][0], info['cell'][1], info['cell'][2],
               info['cell'][1], info['cell'][4], info['cell'][5]))
    print('%.2f %.2f' % mtzdump.get_resolution_range())
