import os
import sys
import math

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'lib'))

# external modules used here

# FIXME add an interrogate_image module - e.g. from fast_dp

from .interrogate_image import interrogate_image

# now import the factories that we will need

from wrappers.mosflm.mosflm_factory import mosflm_factory

# this will -
#
# calculate an inscribed circle resolution
# calculate a native and anomalous strategy

class calculate_strategy:

    def __init__(self):
        self._working_directory = os.getcwd()
        self._mosflm_factory = mosflm_factory()

        self._image = None

        self._interrogate_image = None
        self._images = []

        self._template = None
        self._directory = None
        self._detector = None
        self._matrix = None
        self._spacegroup = None
        self._mosaic = None
        self._anomalous = False

        self._resolution = None

        self._phi_start = None
        self._phi_end = None
        self._phi_width = None

        self._completeness = None

        return

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        self._mosflm_factory.set_working_directory(working_directory)
        return

    def get_working_directory(self):
        return self._working_directory

    def set_image(self, image):
        self._image = image
        self._interrogate_image = interrogate_image()
        self._interrogate_image.set_image(image)
        self._template = self._interrogate_image.get_template()
        self._directory = self._interrogate_image.get_directory()
        return

    def set_detector(self, detector):
        self._detector = detector

    def set_spacegroup(self, spacegroup):
        self._spacegroup = spacegroup
        return

    def set_mosaic(self, mosaic):
        self._mosaic = mosaic
        return

    def set_matrix(self, matrix):
        self._matrix = matrix
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

    def get_resolution(self):
        return self._resolution

    # real methods

    def select_images(self):
        if len(self._interrogate_image.get_images()) < 20:
            self._images = self._interrogate_image.get_images()
        else:
            raise RuntimeError('implement something here')

        return

    def resolution(self):
        ii = self._interrogate_image
        size = ii.get_size()
        pixel = ii.get_pixel()
        d = ii.get_distance()
        l = ii.get_wavelength()

        r = 0.25 * (size[0] * pixel[0] + size[1] * pixel[1])

        theta = 0.5 * math.atan(r / d)

        self._resolution = l / (2 * math.sin(theta))

        return

    def strategy(self):
        ms = self._mosflm_factory.strategy()
        if self._anomalous:
            ms.write_log_file('strategy_anomalous.log')
        else:
            ms.write_log_file('strategy_native.log')
        ii = self._interrogate_image
        if ii.get_goniometer_is_vertical():
            ms.set_omega(270)
        ms.set_matrix(self._matrix)
        ms.set_resolution(self._resolution)
        ms.set_mosaic(self._mosaic)
        ms.set_spacegroup(self._spacegroup)
        ms.set_template(self._template)
        ms.set_directory(self._directory)
        if self._detector:
            ms.set_detector(self._detector)
        if self._anomalous:
            ms.set_anomalous(self._anomalous)
        for image in self._images:
            ms.add_image(image)
        ms.strategy()

        self._phi_start = ms.get_phi_start()
        self._phi_end = ms.get_phi_end()
        self._phi_width = ms.get_phi_width()
        self._completeness = ms.get_completeness()
        return

    def integrate(self):
        ms = self._mosflm_factory.integrate()
        ms.write_log_file('integrate.log')
        ms.set_matrix(self._matrix)
        ms.set_resolution(self._resolution)
        ms.set_mosaic(self._mosaic)
        ms.set_spacegroup(self._spacegroup)
        ms.set_template(self._template)
        ms.set_directory(self._directory)
        if self._anomalous:
            ms.set_anomalous(self._anomalous)
        for image in self._images:
            ms.add_image(image)
        ms.integrate()
        return

    def calculate_strategy(self):

        self.select_images()
        self.resolution()
        self.strategy()
        self.integrate()

        return


if __name__ == '__main__':

    from .characterise_diffraction import characterise_diffraction

    cd = characterise_diffraction()
    cd.set_image(sys.argv[1])
    cd.characterise()

    print('Unit cell: %.3f %.3f %.3f %.3f %.3f %.3f' % cd.get_cell())
    print('Spacegroup: %s' % cd.get_spacegroup())
    print('Mosaic: %.2f' % cd.get_mosaic())

    cs = calculate_strategy()
    cs.set_image(sys.argv[1])
    cs.set_matrix(cd.get_matrix())
    cs.set_spacegroup(cd.get_spacegroup())
    cs.set_mosaic(cd.get_mosaic())
    cs.calculate_strategy()

    print('Native')
    print('Phi range: %.1f to %.1f' % (cs.get_phi_start(), cs.get_phi_end()))
    print('Phi width: %.1f' % cs.get_phi_width())
    print('Completeness: %.2f' % cs.get_completeness())

    cs = calculate_strategy()
    cs.set_image(sys.argv[1])
    cs.set_matrix(cd.get_matrix())
    cs.set_spacegroup(cd.get_spacegroup())
    cs.set_mosaic(cd.get_mosaic())
    cs.set_anomalous(True)
    cs.calculate_strategy()

    print('Anomalous')
    print('Phi range: %.1f to %.1f' % (cs.get_phi_start(), cs.get_phi_end()))
    print('Phi width: %.1f' % cs.get_phi_width())
    print('Completeness: %.2f' % cs.get_completeness())
