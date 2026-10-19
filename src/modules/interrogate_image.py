import os
import sys
import subprocess
import time

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'lib'))

from jiffies.files import image2template, image2image, \
     image2template_directory, \
     find_matching_images, template_directory_number2image
### BODGE ###

# I should implement a proper diffdump wrapper as per xia2.

def run_job(executable, arguments = [], stdin = [], working_directory = None):
    '''Run a program with some command-line arguments and some input,
    then return the standard output when it is finished.'''

    if working_directory is None:
        working_directory = os.getcwd()

    command_line = '%s' % executable
    for arg in arguments:
        command_line += ' "%s"' % arg

    popen = subprocess.Popen(command_line,
                             bufsize = 1,
                             stdin = subprocess.PIPE,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.STDOUT,
                             cwd = working_directory,
                             universal_newlines = True,
                             shell = True)

    for record in stdin:
        popen.stdin.write('%s\n' % record)

    popen.stdin.close()

    output = []

    while True:
        record = popen.stdout.readline()
        if not record:
            break

        output.append(record)

    return output

def get_dectris_serial_no(record):
    if not 'S/N' in record:
        return '0'
    tokens = record.split()
    return tokens[tokens.index('S/N') + 1]

def failover_cbf(cbf_file):
    '''CBF files from the latest update to the PILATUS detector cause a
    segmentation fault in diffdump. This is a workaround.'''

    header = { }

    header['two_theta'] = 0.0

    for record in open(cbf_file, encoding='latin-1'):
        if '_array_data.data' in record:
            break

        if 'PILATUS 2M' in record:
            header['detector_class'] = 'pilatus 2M'
            header['detector'] = 'dectris'
            header['size'] = (1679, 1475)
            header['serial_number'] = get_dectris_serial_no(record)
            continue

        if 'PILATUS 6M' in record:
            header['detector_class'] = 'pilatus 6M'
            header['detector'] = 'dectris'
            header['size'] = (2527, 2463)
            header['serial_number'] = get_dectris_serial_no(record)
            continue

        if 'PILATUS3 6M' in record:
            header['detector_class'] = 'pilatus 6M'
            header['detector'] = 'dectris'
            header['size'] = (2527, 2463)
            header['serial_number'] = get_dectris_serial_no(record)
            continue

        if 'EIGER 16M' in record or 'EIGER 2XE 16M' in record:
            header['detector_class'] = 'eiger 16M'
            header['detector'] = 'dectris'
            header['size'] = (4362, 4148)
            header['serial_number'] = get_dectris_serial_no(record)
            continue

        if 'Start_angle' in record:
            header['phi_start'] = float(record.split()[-2])
            continue

        if 'Angle_increment' in record:
            header['phi_width'] = float(record.split()[-2])
            header['phi_end'] = header['phi_start'] + header['phi_width']
            header['oscillation'] = header['phi_start'], header['phi_width']
            continue

        if 'Exposure_period' in record:
            header['exposure_time'] = float(record.split()[-2])
            continue

        if 'Filter_transmission' in record:
            t = float(record.split()[-1])
            # because sometimes people use percent - what if 0.05%? too bad...
            if t > 1.0:
                t *= 0.01
            header['transmission'] = t
            continue

        if 'Detector_distance' in record:
            header['distance'] = 1000 * float(record.split()[2])
            continue

        if 'Wavelength' in record:
            header['wavelength'] = float(record.split()[-2])
            continue

        if 'Pixel_size' in record:
            header['pixel'] = 1000 * float(record.split()[2]), \
                              1000 * float(record.split()[5])
            continue

        if 'Beam_xy' in record:
            beam_pixels = list(map(float, record.replace('(', '').replace(
                ')', '').replace(',', '').split()[2:4]))
            header['beam'] = beam_pixels[0] * header['pixel'][0], \
                             beam_pixels[1] * header['pixel'][1]
            continue

        # try to get the date etc. literally.

        try:
            datestring = record.split()[-1].split('.')[0]
            format = '%Y-%b-%dT%H:%M:%S'
            struct_time = time.strptime(datestring, format)
            header['date'] = time.asctime(struct_time)
            header['epoch'] = time.mktime(struct_time)

        except Exception as e:
            pass

        try:
            datestring = record.split()[-1].split('.')[0]
            format = '%Y-%m-%dT%H:%M:%S'
            struct_time = time.strptime(datestring, format)
            header['date'] = time.asctime(struct_time)
            header['epoch'] = time.mktime(struct_time)

        except Exception as e:
            pass


        try:
            datestring = record.replace('#', '').strip().split('.')[0]
            format = '%Y/%b/%d %H:%M:%S'
            struct_time = time.strptime(datestring, format)
            header['date'] = time.asctime(struct_time)
            header['epoch'] = time.mktime(struct_time)

        except Exception as e:
            pass

    # cope with vertical goniometer on I24 @ DLS from 2015/1/1
    if header.get('serial_number', '0') == '60-0119' and \
            int(header['date'].split()[-1]) >= 2015 and True:
        header['goniometer_is_vertical'] = True
    else:
        header['goniometer_is_vertical'] = False

    return header

def read_image_metadata(image):
    '''Read the image header and send back the resulting metadata in a
    dictionary.'''

    assert(os.path.exists(image))

    template, directory = image2template_directory(image)
    matching = find_matching_images(template, directory)

    # work around (preempt) diffdump failure with the new 2M instrument

    try:
        if '.cbf' in image[-4:]:
            metadata = failover_cbf(image)
            assert(metadata['detector_class'] in \
                   ['pilatus 2M', 'pilatus 6M', 'eiger 16M'])

            if metadata['detector_class'] == 'pilatus 2M':
                metadata['detector'] = 'PILATUS_2M'
            elif metadata['detector_class'] == 'eiger 16M':
                metadata['detector'] = 'EIGER_16M'
            else:
                metadata['detector'] = 'PILATUS_6M'

            metadata['directory'] = directory
            metadata['template'] = template
            metadata['start'] = min(matching)
            metadata['end'] = max(matching)
            metadata['images'] = matching

            return metadata

    except Exception as e:
        pass


    # MAR CCD images record the beam centre in pixels...

    diffdump_output = run_job('diffdump', arguments = [image])

    metadata = { }

    for record in diffdump_output:
        if 'Wavelength' in record:
            wavelength = float(record.split()[-2])
            metadata['wavelength'] = wavelength

        elif 'Beam center' in record:
            x = float(record.replace('(', ' ').replace(
                'mm', ' ').replace(',', ' ').split()[3])
            y = float(record.replace('(', ' ').replace(
                'mm', ' ').replace(',', ' ').split()[4])
            metadata['beam'] = x, y

        elif 'Image Size' in record:
            x = int(record.replace('(', ' ').replace(
                'px', ' ').replace(',', ' ').split()[3])
            y = int(record.replace('(', ' ').replace(
                'px', ' ').replace(',', ' ').split()[4])
            metadata['size'] = x, y

        elif 'Pixel Size' in record:
            x = float(record.replace('(', ' ').replace(
                'mm', ' ').replace(',', ' ').split()[3])
            y = float(record.replace('(', ' ').replace(
                'mm', ' ').replace(',', ' ').split()[4])
            metadata['pixel'] = x, y

        elif 'Distance' in record:
            distance = float(record.split()[-2])
            metadata['distance'] = distance

        elif 'Oscillation' in record:
            phi_start = float(record.split()[3])
            phi_end = float(record.split()[5])
            phi_width = phi_end - phi_start

            if phi_width > 360.0:
                phi_width -= 360.0

            metadata['oscillation'] = phi_start, phi_width

        elif 'Manufacturer' in record or 'Image type' in record:
            detector = record.split()[-1]
            if detector == 'ADSC':
                metadata['detector'] = 'ADSC'
            elif detector == 'MAR':
                metadata['detector'] = 'MARCCD'
            elif detector == 'DECTRIS':
                metadata['detector'] = 'PILATUS_6M'
            else:
                raise RuntimeError('detector %s not yet supported' % \
                      detector)

    if (metadata['detector'] == 'PILATUS_6M') and \
       (metadata['size'] == (1679, 1475)):
                metadata['detector'] = 'PILATUS_2M'

    # now compute the filename template and what have you, and also
    # verify that the results stored make sense, particularly w.r.t.
    # the beam centre, which may be stored in pixels not mm.

    template, directory = image2template_directory(image)
    matching = find_matching_images(template, directory)
    metadata['images'] = matching

    # MAR CCD images record the beam centre in pixels...

    if metadata['detector'] == 'MARCCD':
        metadata['beam'] = (metadata['beam'][0] * metadata['pixel'][0],
                            metadata['beam'][1] * metadata['pixel'][1])

    metadata['directory'] = directory
    metadata['template'] = template
    metadata['start'] = min(matching)
    metadata['end'] = max(matching)

    return metadata

class interrogate_image:

    def __init__(self):

        self._image = None
        self._metadata = None

        return

    def set_image(self, image):
        self._image = image
        self._metadata = read_image_metadata(image)
        return

    def get_beam(self):
        return self._metadata['beam']

    def get_size(self):
        return self._metadata['size']

    def get_pixel(self):
        return self._metadata['pixel']

    def get_distance(self):
        return self._metadata['distance']

    def get_wavelength(self):
        return self._metadata['wavelength']

    def get_phi_start(self):
        return self._metadata['oscillation'][0]

    def get_phi_end(self):
        return self._metadata['oscillation'][1]

    def get_exposure_time(self):
        return self._metadata['exposure_time']

    def get_transmission_percent(self):
        return 100 * self._metadata.get('transmission', 1.0)

    def get_images(self):
        return self._metadata['images']

    def get_template(self):
        return self._metadata['template']

    def get_directory(self):
        return self._metadata['directory']

    def get_goniometer_is_vertical(self):
        return self._metadata.get('goniometer_is_vertical', False)

    def get_detector_class(self):
        return self._metadata.get('detector_class', '')

if __name__ == '__main__':

    ii = interrogate_image()

    ii.set_image(sys.argv[1])

    print(ii.get_template())
    print(ii.get_directory())
    print(ii.get_images())
    print(ii.get_distance())
    print(ii.get_wavelength())
