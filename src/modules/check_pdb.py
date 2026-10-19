import os
import sys

if not 'CCP4' in os.environ:
    raise RuntimeError('CCP4 undefined')

class check_pdb:
    '''A class to check that the ligands in a PDB file all appear in the
    CCP4 monomer dictionary. Will also check for a CRYST1 record.'''

    def __init__(self):

        self._known_monomers = []

        monomer = os.path.join(os.environ['CCP4'], 'lib', 'data', 'monomers')

        for dirpath, dirnames, filenames in os.walk(monomer):
            for filename in filenames:
                self._known_monomers.append(filename.replace('.cif', ''))

        return

    def check_pdb(self, pdb_file):
        '''Check a PDB file that all of the ATOM and HETATM records belong
        to a known ligand or residue.'''

        unknown = []

        CRYST1 = False

        for record in open(pdb_file):

            if 'CRYST1' in record:
                CRYST1 = True

            if 'ATOM  ' in record[:6] or 'HETATM' in record[:6]:
                residue = record[17:20]

                if not residue in self._known_monomers:
                    unknown.append(residue)

        if unknown:
            unknown_residues = unknown[0]
            for m in unknown_residues[1:]:
                unknown_residues += ' %s' % m
            raise RuntimeError('Unknown residues: %s' % unknown_residues)

        if not CRYST1:
            raise RuntimeError('CRYST1 record not found')

        return

if __name__ == '__main__':

    cpl = check_pdb()

    if len(sys.argv) < 2:
        raise RuntimeError('%s file.pdb [...]' % sys.argv[0])

    for arg in sys.argv[1:]:
        print(arg)
        try:
            cpl.check_pdb(arg)
            print('ok')
        except Exception as e:
            print(e)
