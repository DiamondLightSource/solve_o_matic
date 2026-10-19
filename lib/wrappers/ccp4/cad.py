import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory
from Decorators.DecoratorFactory import DecoratorFactory

from .mtzdump import Mtzdump

def Cad(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)
    CCP4DriverInstance = DecoratorFactory.Decorate(DriverInstance, 'ccp4')

    class CadWrapper(CCP4DriverInstance.__class__):

        def __init__(self):
            # generic things
            CCP4DriverInstance.__class__.__init__(self)
            self.set_executable('cad')

            # N.B. Since CAD takes more than one input file the
            # ccp4 decorator hklin is not helpful...
            self._hklin_files = []

            # optional assignment of new cell constants (i.e. for MAD
            # experiments) or updating the column names.
            self._cell_parameters = None
            self._column_suffix = None

            # assignment of project / crystal / dataset
            self._pname = None
            self._xname = None
            self._dname = None

            # stuff to specifically copy in the freer column...
            self._freein = None
            self._freein_column = 'FreeR_flag'

        # overload the set_hklin() method as this will not work with
        # CAD...

        def set_hklin(self, hklin):
            raise RuntimeError('cannot use set_hklin with Cad wrapper')

        def add_hklin(self, hklin):
            self._hklin_files.append(hklin)
            return

        def set_freein(self, freein, freein_column = 'FreeR_flag'):
            if not os.path.exists(freein):
                raise RuntimeError('%s does not exist' % freein)

            # FIXME should really check that the column is in the free file.

            self._freein = freein
            self._freein_column = freein_column

            return

        def set_project_info(self, pname, xname, dname):
            self._pname = pname
            self._xname = xname
            self._dname = dname
            return

        def set_new_suffix(self, suffix):
            self._column_suffix = suffix
            return

        def set_new_cell(self, cell):
            self._cell_parameters = cell
            return

        # three real "doing" methods for this one - merge() to merge the files
        # in the hklin list and update() to change properties of one file
        # (which should be assigned as HKLIN) and copyfree() to copy the
        # FreeR_flag column from freein to hklout with the columns
        # from hklin

        def merge(self):

            if not self._hklin_files:
                raise RuntimeError('no hklin files defined')

            self.check_hklout()

            hklin_counter = 0

            # for each reflection file, need to gather the column names
            # and so on, to put in the cad input here - also check to see
            # if the column names clash... check also that the spacegroups
            # match up...

            symmetry = None
            column_names = []
            column_names_by_file = { }

            for hklin in self._hklin_files:
                mtzdump = Mtzdump()
                mtzdump.set_working_directory(self.get_working_directory())
                mtzdump.set_hklin(hklin)
                mtzdump.dump()
                columns = mtzdump.get_columns()
                this_symmetry = mtzdump.get_symmetry()

                if symmetry is None:
                    symmetry = this_symmetry

                if this_symmetry != symmetry:
                    raise RuntimeError('spacegroups do not match')

                column_names_by_file[hklin] = []

                for c in columns:
                    name = c[0]
                    if name in ['H', 'K', 'L']:
                        continue
                    if name in column_names:
                        raise RuntimeError('duplicate column names')
                    column_names.append(name)
                    column_names_by_file[hklin].append(name)

            # create the command line

            hklin_counter = 0
            for hklin in self._hklin_files:
                hklin_counter += 1
                self.add_command_line('hklin%d' % hklin_counter)
                self.add_command_line(hklin)

            self.start()

            hklin_counter = 0

            for hklin in self._hklin_files:
                column_counter = 0
                hklin_counter += 1
                labin_command = 'labin file_number %d' % hklin_counter
                for column in column_names_by_file[hklin]:
                    column_counter += 1
                    labin_command += ' E%d=%s' % (column_counter, column)

                self.input(labin_command)

            self.close_wait()

            self.check_for_errors()
            self.check_ccp4_errors()

            return

        def update(self):

            if not self._hklin_files:
                raise RuntimeError('no hklin files defined')

            if len(self._hklin_files) > 1:
                raise RuntimeError('can have only one hklin to update')

            hklin = self._hklin_files[0]

            self.check_hklout()

            column_names_by_file = { }
            dataset_names_by_file = { }

            mtzdump = Mtzdump()
            mtzdump.set_hklin(self._hklin)
            mtzdump.dump()
            columns = mtzdump.get_columns()

            column_names_by_file[hklin] = []
            dataset_names_by_file[hklin] = mtzdump.get_datasets()

            dataset_ids = [mtzdump.get_dataset_info(d)['id'] for \
                           d in mtzdump.get_datasets()]

            for c in columns:
                name = c[0]
                if name in ['H', 'K', 'L']:
                    continue

                column_names_by_file[hklin].append(name)

            self.add_command_line('hklin1')
            self.add_command_line(hklin)
            self.start()

            dataset_id = dataset_ids[0]

            if self._pname and self._xname and self._dname:
                self.input('drename file_number 1 %d %s %s' % \
                           (dataset_id, self._xname, self._dname))
                self.input('dpname file_number 1 %d %s' % \
                           (dataset_id, self._pname))

            column_counter = 0
            labin_command = 'labin file_number 1'
            for column in column_names_by_file[hklin]:
                column_counter += 1
                labin_command += ' E%d=%s' % (column_counter, column)

            self.input(labin_command)

            pname, xname, dname = dataset_names_by_file[hklin][0].split('/')
            dataset_id = dataset_ids[0]

            if self._cell_parameters:
                a, b, c, alpha, beta, gamma = self._cell_parameters
                self.input('dcell file_number 1 %d %f %f %f %f %f %f' % \
                           (dataset_id, a, b, c, alpha, beta, gamma))

            if self._column_suffix:
                suffix = self._column_suffix
                column_counter = 0
                labout_command = 'labout file_number 1'
                for column in column_names_by_file[hklin]:
                    column_counter += 1
                    labout_command += ' E%d=%s_%s' % \
                                     (column_counter, column, suffix)

                self.input(labout_command)

            self.close_wait()

            self.check_for_errors()
            self.check_ccp4_errors()

            return

        def copyfree(self):
            if not self._hklin_files:
                raise RuntimeError('no hklin files defined')

            if len(self._hklin_files) > 1:
                raise RuntimeError('can have only one hklin to update')

            hklin = self._hklin_files[0]

            self.check_hklout()
            if self._freein is None:
                raise RuntimeError('freein not defined')
            if self._freein_column is None:
                raise RuntimeError('freein column not defined')

            self.add_command_line('hklin1')
            self.add_command_line(self._freein)
            self.add_command_line('hklin2')
            self.add_command_line(hklin)
            self.start()

            self.input('labin file_number 1 E1=%s' % self._freein_column)
            self.input('labin file_number 2 all')

            self.close_wait()

            self.check_for_errors()
            self.check_ccp4_errors()

            return

    return CadWrapper()

if __name__ == '__main__':
    # really need to figure out how to write a test here...

    pass
