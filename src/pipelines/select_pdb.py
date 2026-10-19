# tool to select the right pdb file to use for a difference map calculation

import os
import sys
import math

if not 'SOM_ROOT' in os.environ:
    raise RuntimeError('SOM_ROOT undefined')

if not os.environ['SOM_ROOT'] in sys.path:
    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'src'))

from modules.module_factory import module_factory

from dimple import ersatz_pointgroup

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
        try:
            ip.interrogate_pdb()
            if reference == ersatz_pointgroup(ip.get_symmetry_full()):
                candidates.append(xyzin)
                if reference == 'P222':
                    cells[xyzin] = nearest_orthorhombic(reference_cell,
                                                        ip.get_cell())
                else:
                    cells[xyzin] = ip.get_cell()
        except RuntimeError as e:
            sys.stderr.write('%s\n' % e)
            continue


    if len(candidates) == 0:
        return None
    elif len(candidates) == 1:
        return candidates[0]

    # then if there are more than one, see if one matches closer than
    # the others... do this by sorting on the absolute differences in
    # cell constants then picking the closest match

    diffs = []

    for xyzin in candidates:
        diff = sum([math.fabs(reference_cell[j] - cells[xyzin][j]) \
                    for j in range(6)])
        diffs.append((diff, xyzin))

    diffs.sort()

    return diffs[0][1]

def nearest_orthorhombic(ref_cell, test_cell):
    '''Test for alternative indexing possibilities for an orthorhombic
    primitive lattice, to handle e.g. P21221 vs. P21212.'''

    for j in 3, 4, 5:
        if int(round(ref_cell[j])) != 90:
            return None

    for j in 3, 4, 5:
        assert(int(round(test_cell[j])) == 90)

    a, b, c = tuple(test_cell[:3])

    best = a * a + b * b * c * c
    best_cell = None

    # try permuting the cell axes

    for test, reindex in ((a, b, c), 'h,k,l'), \
            ((b, c, a), 'k,l,h'), \
            ((c, a, b), 'l,h,k'):

        diff = sum(
            [(test[j] - ref_cell[j]) * (test[j] - ref_cell[j]) \
             for j in range(3)])

        if diff < best:
            best = diff
            best_cell = test

    return best_cell[0], best_cell[1], best_cell[2], 90, 90, 90

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

    for arg in sys.argv[1:]:
        if os.path.split(arg)[-1].split('.')[0] in os.getcwd():
            candidates.append(arg)

    if len(candidates) == 0:
        sys.exit(0)

    hklin = 'fast_dp.mtz'

    try:
        xyzin = select_right_pdb(hklin, candidates)
    except RuntimeError as e:
        sys.stderr.write('%s\n' % e)
        sys.exit(1)

    if xyzin:
        print('%s' % xyzin)
