import os
import sys

if not 'CCP4' in os.environ:
    raise RuntimeError('CCP4 undefined')

class edit_pdb:
    '''A class to edit a pdb file to remove named ligands & monomers, or just
    leave in known ones..'''

    def __init__(self):

        self._known_monomers = []

        monomer = os.path.join(os.environ['CCP4'], 'lib', 'data', 'monomers')

        for dirpath, dirnames, filenames in os.walk(monomer):
            for filename in filenames:
                self._known_monomers.append(filename.replace('.cif', ''))

        return

    def edit_pdb(self, xyzin, xyzout, monomers_to_remove = None):
        '''Edit a PDB file to remove all of the ATOM and HETATM records
        belonging to the listed monomers. If monomers_to_remove is not
        specified, then just remove those that are not in the CCP4 monomer
        database. N.B. this will not modify anything but the ATOM / HETATM
        records.'''

        pdb_records = open(xyzin).readlines()
        remove = []

        if monomers_to_remove:

            for j, record in enumerate(pdb_records):

                if 'ATOM  ' in record[:6] or 'HETATM' in record[:6]:
                    residue = record[17:20]

                    if residue in monomers_to_remove:
                        remove.append(j)
                        if 'ANISOU' in pdb_records[j + 1][:6]:
                            remove.append(j + 1)

        else:
            for j, record in enumerate(pdb_records):

                if 'ATOM  ' in record[:6] or 'HETATM' in record[:6]:
                    residue = record[17:20]

                    if not residue in self._known_monomers:
                        remove.append(j)
                        if 'ANISOU' in pdb_records[j + 1][:6]:
                            remove.append(j + 1)

        # now write out the records...

        fout = open(xyzout, 'w')

        for j, record in enumerate(pdb_records):
            if j in remove:
                continue
            fout.write(record)

        return

if __name__ == '__main__':

    ep = edit_pdb()

    if len(sys.argv) < 3:
        raise RuntimeError('%s xyzin xyzout [monomers to remove]' % \
              sys.argv[0])

    ep.edit_pdb(sys.argv[1], sys.argv[2], sys.argv[3:])
