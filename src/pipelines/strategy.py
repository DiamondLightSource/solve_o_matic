# strategy pipeline customised to work at Diamond...

import os
import sys
import math

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'src'))

# import the modules that we will need

from modules.module_factory import module_factory

class strategy_pipeline:

    def __init__(self):

        self._working_directory = os.getcwd()
        self._factory = module_factory()
        self._image = None

        self._matrix = None
        self._spacegroup = None
        self._cell = None
        self._mosaic = None

        self._phi_start = None
        self._phi_end = None
        self._phi_width = None

        self._completeness = None

        self._resolution = None

        return

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        self._ccp4_factory.set_working_directory(working_directory)
        return

    def get_working_directory(self):
        return self._working_directory

    def set_image(self, image):
        self._image = image
        return

    def set_spacegroup(self, spacegroup):
        self._spacegroup = spacegroup
        return

    def get_spacegroup(self):
        return self._spacegroup

    def get_cell(self):
        return self._cell

    def get_mosaic(self):
        return self._mosaic

    def get_matrix(self):
        return self._matrix

    def get_phi_start(self):
        return self._phi_start

    def get_phi_end(self):
        return self._phi_end

    def get_phi_width(self):
        return self._phi_width

    def get_n_images(self):
        return self._n_images

    def get_completeness(self):
        return self._completeness

    def get_resolution(self):
        return self._resolution

    def strategy_pipeline_characterise(self):

        assert(self._image)

        cd = self._factory.characterise_diffraction()
        cd.set_image(self._image)
        if self._spacegroup:
            cd.set_spacegroup(self._spacegroup)
        cd.characterise()

        self._cell = cd.get_cell()
        self._spacegroup = cd.get_spacegroup()
        self._mosaic = cd.get_mosaic()
        self._matrix = cd.get_matrix()
        self._detector = cd.get_detector()

    def strategy_pipeline_strategy(self, anomalous = False):

        assert(self._spacegroup != None)

        cs = self._factory.calculate_strategy()
        cs.set_image(self._image)
        cs.set_matrix(self._matrix)
        cs.set_spacegroup(self._spacegroup)
        cs.set_mosaic(self._mosaic)
        cs.set_anomalous(anomalous)
        if self._detector:
            cs.set_detector(self._detector)
        cs.calculate_strategy()

        self._phi_start = cs.get_phi_start()
        self._phi_end = cs.get_phi_end()
        self._phi_width = cs.get_phi_width()
        self._completeness = cs.get_completeness()
        self._resolution = cs.get_resolution()

        # derived things

        phi_range = self._phi_end - self._phi_start

        if phi_range < 0.0:
            phi_range += 360.0

        self._n_images = int(phi_range / self._phi_width)

        if self._n_images * self._phi_width < phi_range:
            self._n_images += 1

        return

# helper functions

def write_dat_file(character, native, anomalous):
    dat_file = open('strategy.dat', 'w')
    dat_file.write('character,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,' % character[0])
    dat_file.write('%s,%.2f\n' % (character[1], character[2]))
    dat_file.write('mosflm native,%.1f,%.1f,%.1f,%d,%.2f,%.2f\n' % native)
    dat_file.write('mosflm anomalous,%.1f,%.1f,%.1f,%d,%.2f,%.2f\n' % \
                   anomalous)
    dat_file.close()
    return

def write_html_file(image, character, native, anomalous):
    html_file = open('strategy.html', 'w')
    template = open(os.path.join(os.environ['SOM_ROOT'], 'lib', 'templates',
                                 'strategy_html_template.html')).read()

    text = template.format(image = image,
                           cell_a = character[0][0],
                           cell_b = character[0][1],
                           cell_c = character[0][2],
                           cell_alpha = character[0][3],
                           cell_beta = character[0][4],
                           cell_gamma = character[0][5],
                           spacegroup = character[1],
                           mosaic = character[2],
                           phi_start_n = native[0],
                           phi_end_n = native[1],
                           phi_width_n = native[2],
                           n_images_n = native[3],
                           completeness_n = native[4],
                           resolution_n = native[5],
                           phi_start_a = anomalous[0],
                           phi_end_a = anomalous[1],
                           phi_width_a = anomalous[2],
                           n_images_a = anomalous[3],
                           completeness_a = anomalous[4],
                           resolution_a = anomalous[5])

    html_file.write(text)
    html_file.close()
    return

if __name__ == '__main__':

    if len(sys.argv) < 2:
        raise RuntimeError('%s /path/to/one/image [spacegroup]' % sys.argv[0])

    sp = strategy_pipeline()
    sp.set_image(sys.argv[1])

    if len(sys.argv) > 2:
        sp.set_spacegroup(sys.argv[2])

    sp.strategy_pipeline_characterise()
    sp.strategy_pipeline_strategy()

    print('Unit cell: %.3f %.3f %.3f %.3f %.3f %.3f' % sp.get_cell())
    print('Spacegroup: %s' % sp.get_spacegroup())
    print('Mosaic: %.2f' % sp.get_mosaic())

    character = (sp.get_cell(), sp.get_spacegroup(), sp.get_mosaic())

    print('Native strategy:')
    print('Phi range: %.1f to %.1f' % (sp.get_phi_start(), sp.get_phi_end()))
    print('Phi width: %.1f' % sp.get_phi_width())
    print('No. images: %d' % sp.get_n_images())
    print('Completeness: %.2f' % sp.get_completeness())
    print('Resolution:   %.2f' % sp.get_resolution())

    native = (sp.get_phi_start(), sp.get_phi_end(), sp.get_phi_width(),
              sp.get_n_images(), sp.get_completeness(), sp.get_resolution())

    sp.strategy_pipeline_strategy(anomalous = True)
    print('Anomalous strategy:')
    print('Phi range: %.1f to %.1f' % \
          (sp.get_phi_start(), sp.get_phi_end()))
    print('Phi width: %.1f' % sp.get_phi_width())
    print('No. images: %d' % sp.get_n_images())
    print('Completeness: %.2f' % sp.get_completeness())
    print('Resolution:   %.2f' % sp.get_resolution())

    anomalous = (sp.get_phi_start(), sp.get_phi_end(), sp.get_phi_width(),
                 sp.get_n_images(), sp.get_completeness(), sp.get_resolution())

    write_dat_file(character, native, anomalous)

    if len(sys.argv) > 2:
        spacegroup = '%s (ispyb)' % sp.get_spacegroup()
    else:
        spacegroup = sp.get_spacegroup()

    character = (sp.get_cell(), spacegroup, sp.get_mosaic())

    write_html_file(os.path.split(sys.argv[1])[-1],
                    character, native, anomalous)
