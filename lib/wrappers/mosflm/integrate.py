import os
import sys

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Driver.DriverFactory import DriverFactory

def Mosflm_integrate(DriverType = None):

    DriverInstance = DriverFactory.Driver(DriverType)

    class Mosflm_integrateWrapper(DriverInstance.__class__):

        def __init__(self):
            # generic things
            DriverInstance.__class__.__init__(self)
            self.set_executable('ipmosflm')

            self._template = None
            self._directory = None
            self._beam = None
            self._limits_dict = { }
            self._images = []
            self._spacegroup = None
            self._mosaic = None
            self._matrix = None
            self._resolution = None

            return

        def set_template(self, template):
            self._template = template
            return

        def set_directory(self, directory):
            self._directory = directory
            return

        def set_beam(self, beam):
            self._beam = beam
            return

        def set_limits_dict(self, limits_dict):
            self._limits_dict = limits_dict
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

        def integrate(self):
            assert(self._template != None)
            assert(self._directory != None)
            assert(self._spacegroup != None)
            assert(self._resolution != None)
            assert(self._matrix != None)
            assert(self._images != [])

            self.start()

            if self._limits_dict:
                c0 = 'xmin {xmin} xmax {xmax} ymin {ymin} ymax {ymax}'.format(
                    **self._limits_dict)
                c1 = 'rmin {rmin} rmax {rmax}'.format(
                    **self._limits_dict)
                c2 = 'xscan {xscan} yscan {yscan}'.format(
                    **self._limits_dict)
                self.input('limits %s' % c0)
                self.input('limits %s' % c1)
                self.input('limits %s' % c2)

            self.input('symmetry %s' % self._spacegroup)
            self.input('matrix %s' % self._matrix)
            self.input('template %s' % self._template)
            if self._beam:
                self.input('beam %f %f' % self._beam)
            self.input('directory %s' % self._directory)
            if '.cbf' in self._template[-4:]:
                self.input('detector pilatus')
            self.input('findspots find %s' % self._images[0])
            self.input('go')
            self.input('mosaic %f' % self._mosaic)
            if self._resolution:
                self.input('resolution %f' % self._resolution)
            self.input('postref fix all')
            self.input('best on')
            for image in self._images:
                self.input('process %d %d' % (image, image))
                self.input('go')
            self.close_wait()

            # now pull out the output... though don't really want this

            for record in self.get_all_output():
                pass

            # do want to chmod the files bestfile.par and bestfile.hkl
            for f in 'bestfile.par', 'bestfile.hkl':
                try:
                    os.chmod(os.path.join(self.get_working_directory(), f),
                             0o644)
                except:
                    pass


            return

    return Mosflm_integrateWrapper()


if __name__ == '__main__':

    ms = Mosflm_integrate()

    ms.set_matrix('mosflm_index.mat')
    ms.set_resolution(1.6)
    ms.set_mosaic(0.25)
    ms.set_spacegroup('P4')
    ms.set_template('thaumatin_die_M1S5_1_####.img')
    ms.set_directory(
        '/dls/mx-scratch/gw56/drives/1/dls/dna/nt1956-6/thaumatin_die')
    for image in [1, 45, 90]:
        ms.add_image(image)
    ms.integrate()
