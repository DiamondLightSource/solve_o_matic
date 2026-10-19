import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory

def Mosflm_strategy(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)

    class Mosflm_strategyWrapper(DriverInstance.__class__):

        def __init__(self):
            # generic things
            DriverInstance.__class__.__init__(self)
            self.set_executable('ipmosflm')

            self._template = None
            self._directory = None
            self._detector = None
            self._images = []
            self._spacegroup = None
            self._mosaic = None
            self._anomalous = False
            self._matrix = None
            self._resolution = None

            self._phi_start = None
            self._phi_end = None
            self._phi_width = None

            self._completeness = None
            self._omega = 0

            return

        def set_template(self, template):
            self._template = template
            return

        def set_directory(self, directory):
            self._directory = directory
            return

        def set_detector(self, detector):
            self._detector = detector
            return

        def add_image(self, image):
            self._images.append(image)
            return

        def set_spacegroup(self, spacegroup):
            self._spacegroup = spacegroup
            return

        def set_resolution(self, resolution):
            self._resolution = resolution

        def set_mosaic(self, mosaic):
            self._mosaic = mosaic
            return

        def set_matrix(self, matrix):
            if self.get_working_directory() in matrix:
                matrix = matrix.replace(self.get_working_directory(), '.')
            self._matrix = matrix
            return

        def set_omega(self, omega):
            self._omega = omega
            return

        def set_anomalous(self, anomalous = True):
            self._anomalous = anomalous
            return

        def get_phi_start(self):
            return self._phi_start

        def get_phi_end(self):
            return self._phi_end

        def get_phi_width(self):
            return self._phi_width

        def get_completeness(self):
            return self._completeness

        def strategy(self):
            assert(self._template != None)
            assert(self._directory != None)
            assert(self._spacegroup != None)
            assert(self._resolution != None)
            assert(self._matrix != None)
            assert(self._images != [])

            self.start()
            self.input('symmetry %s' % self._spacegroup)
            self.input('matrix %s' % self._matrix)
            self.input('template %s' % self._template)
            self.input('directory %s' % self._directory)
            if self._detector:
                self.input('detector %s' % self._detector)
            elif '.cbf' in self._template[-4:]:
                self.input('detector pilatus')
            if self._omega:
                self.input('detector omega %d' % self._omega)

            self.input('findspots find %s' % self._images[0])
            self.input('go')
            self.input('mosaic %f' % self._mosaic)
            if self._resolution:
                self.input('resolution %f' % self._resolution)
            if self._anomalous:
                self.input('strategy testgen anomalous overlap 0.5')
            else:
                self.input('strategy testgen overlap 0.5')
            self.input('go')
            self.close_wait()

            # now pull out the output...

            save_phi_width = False
            phi_widths = []

            for record in self.get_all_output():
                if 'From' in record and 'to' in record and 'degrees' in record:
                    self._phi_start = float(record.split()[1])
                    self._phi_end = float(record.split()[3])

                if 'Phi start' in record and 'no of images' in record:
                    save_phi_width = True
                    continue

                if save_phi_width:
                    if record.strip():
                        phi_widths.append(float(record.split()[3]))
                    else:
                        save_phi_width = False
                        self._phi_width = min(phi_widths)

                if 'Optimum rotation' in record:
                    self._completeness = 0.01 * float(
                        record.replace('%', '').split()[3])

            return


    return Mosflm_strategyWrapper()


if __name__ == '__main__':

    ms = Mosflm_strategy()

    ms.set_matrix('mosflm_index.mat')
    ms.set_resolution(1.6)
    ms.set_mosaic(0.25)
    ms.set_spacegroup('P4')
    ms.set_template('thaumatin_die_M1S5_1_####.img')
    ms.set_directory(
        '/dls/mx-scratch/gw56/drives/1/dls/dna/nt1956-6/thaumatin_die')
    for image in [1, 45, 90]:
        ms.add_image(image)
    ms.strategy()

    print('Native')
    print('Phi range: %.1f to %.1f' % (ms.get_phi_start(), ms.get_phi_end()))
    print('Phi width: %.1f' % ms.get_phi_width())
    print('Completeness: %.2f' % ms.get_completeness())

    ms = Mosflm_strategy()

    ms.set_anomalous(True)
    ms.set_matrix('mosflm_index.mat')
    ms.set_resolution(1.6)
    ms.set_mosaic(0.25)
    ms.set_spacegroup('P4')
    ms.set_template('thaumatin_die_M1S5_1_####.img')
    ms.set_directory(
        '/dls/mx-scratch/gw56/drives/1/dls/dna/nt1956-6/thaumatin_die')
    for image in [1, 45, 90]:
        ms.add_image(image)
    ms.strategy()

    print('Anomalous')
    print('Phi range: %.1f to %.1f' % (ms.get_phi_start(), ms.get_phi_end()))
    print('Phi width: %.1f' % ms.get_phi_width())
    print('Completeness: %.2f' % ms.get_completeness())
