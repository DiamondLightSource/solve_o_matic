# tool to select the right pdb file to use for a difference map calculation

import os
import sys
import math

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'src'))

from modules.module_factory import module_factory

# function to guess the point group

def ersatz_pointgroup(spacegroup):

    result = ''

    for token in spacegroup.split():
        result += token[0]

    return result

# add a function in here to select the right PDB file - defined as having
# something in common name-wise and having the same pointgroup

def select_right_pdb(hklin, pdb_list):
    '''Find a coordinate file which appears to have the right symmetry.'''

    candidates = []

    im = module_factory().interrogate_mtz()
    im.set_hklin(hklin)
    im.interrogate_mtz()
    reference = ersatz_pointgroup(im.get_symmetry())

    reference_cell = im.get_cell()

    cells = { }

    for xyzin in pdb_list:
        ip = module_factory().interrogate_pdb()
        ip.set_xyzin(xyzin)
        ip.interrogate_pdb()
        if reference == ersatz_pointgroup(ip.get_symmetry_full()):
            candidates.append(xyzin)
            cells[xyzin] = ip.get_cell()

    if len(candidates) == 0:
        raise RuntimeError('no matching coordinate files found')

    # then if there are more than one, see if one matches closer than
    # the others... do this by sorting on the absolute differences in
    # cell constants then picking the closest match

    # erm. doesn't this need to consider permutations for P222?

    if len(candidates) == 1:
        return candidates[0]

    diffs = []

    for xyzin in candidates:
        diff = sum([math.fabs(reference_cell[j] - cells[xyzin][j]) \
                    for j in range(6)])
        diffs.append((diff, xyzin))

    diffs.sort()

    return diffs[0][1]

# then add a function to determine (if possible) the right reindexing
# operation for orthorhombic spacegroups

def test_orthorhombic(ref_cell, test_cell):
    '''Test for alternative indexing possibilities for an orthorhombic
    primitive lattice, to handle e.g. P21221 vs. P21212.'''

    for j in 3, 4, 5:
        if int(round(ref_cell[j])) != 90:
            return None

    for j in 3, 4, 5:
        assert(int(round(test_cell[j])) == 90)

    a, b, c = tuple(test_cell[:3])

    best = a * a + b * b * c * c
    best_rdx = None

    # try permuting the cell axes

    for test, reindex in ((a, b, c), 'h,k,l'), \
            ((b, c, a), 'k,l,h'), \
            ((c, a, b), 'l,h,k'):

        diff = sum(
            [(test[j] - ref_cell[j]) * (test[j] - ref_cell[j]) \
             for j in range(3)])

        if diff < best:
            best = diff
            best_rdx = reindex

    assert(best_rdx)

    return best_rdx

# then add a function which will run pointless

if __name__ == '__main__':

    xyzin = None

    candidates = []

    for arg in sys.argv[2:]:
        candidates.append(arg)

    if len(candidates) == 0:
        raise RuntimeError('no candidate pdb files matched %s' % os.getcwd())

    hklin = sys.argv[1]

    try:
        xyzin = select_right_pdb(hklin, candidates)
    except RuntimeError as e:
        xyzin = None

    if not xyzin:
        print('No files found')
    else:
        print('%s' % xyzin)
