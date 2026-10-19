import os
import sys

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'lib'))

# N.B. definition of CRYST1 record from
# http://www.rcsb.org/robohelp/files_formats/structures/pdb/\
# coordinate_file_description/cryst1.htm

class interrogate_pdb:

    def __init__(self):
        self._working_directory = os.getcwd()

        self._xyzin = None

        # return results

        self._cell = None
        self._symmetry = None
        self._sequence = []

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory
        return

    def get_working_directory(self):
        return self._working_directory

    def set_xyzin(self, xyzin):
        self._xyzin = xyzin
        return

    def interrogate_pdb(self):
        cell = None
        symmetry = None

        if not self._xyzin:
            raise RuntimeError('xyzin not defined')

        sequence = { }

        for record in open(self._xyzin):
            if 'CRYST1' in record[:6]:
                cell = list(map(float, record[6:54].split()))
                symmetry = record[55:66].strip()

                continue

            if 'SEQRES' in record[:6] and False:
                for token in record[19:].split():
                    self._sequence.append(token)

            if 'ATOM' in record[:4]:
                res = record[17:20]

                if not res in ['CYS', 'ASP', 'SER', 'GLN', 'LYS', 'ILE',
                               'PRO', 'THR', 'PHE', 'ALA', 'GLY', 'HIS',
                               'GLU', 'LEU', 'ARG', 'TRP', 'VAL', 'ASN',
                               'TYR', 'MET']:
                    continue

                n = int(record[22:26])
                sequence[n] = res

        if not cell or not symmetry:
            raise RuntimeError('CRYST1 record not found in %s' % self._xyzin)

        self._cell = tuple(cell)
        self._symmetry = symmetry

        self._sequence = []

        for n in sorted(sequence):
            self._sequence.append(sequence[n])

        return

    def get_cell(self):
        return self._cell

    def get_symmetry(self):
        return self._symmetry.replace(' ', '')

    def get_symmetry_full(self):
        return self._symmetry

    def get_sequence(self):
        return self._sequence

    def get_molecular_weight(self):

        weights = {'CYS': 121, 'ASP': 133, 'SER': 105, 'GLN': 146,
                   'LYS': 146, 'ASN': 132, 'PRO': 115, 'THR': 119,
                   'PHE': 165, 'ALA': 89, 'HIS': 155, 'GLY': 0,
                   'ILE': 131, 'LEU': 131, 'ARG': 174, 'TRP': 204,
                   'VAL': 117, 'GLU': 147, 'TYR': 181, 'MET': 149}

        weight = 0

        for residue in self._sequence:
            weight += weights[residue]

        return weight

if __name__ == '__main__':

    im = interrogate_pdb()

    if len(sys.argv) < 2:
        im.set_xyzin(os.path.join(os.environ['SOM_ROOT'], 'data',
                                  'insulin.pdb'))

    else:
        im.set_xyzin(sys.argv[1])


    im.interrogate_pdb()
    print(im.get_symmetry_full())
    print(im.get_molecular_weight())
