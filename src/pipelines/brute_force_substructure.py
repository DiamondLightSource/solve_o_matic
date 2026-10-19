import os
import sys

#if not 'SOM_ROOT' in os.environ:
#    raise RuntimeError, 'SOM_ROOT undefined'
#
#if not os.environ['SOM_ROOT'] in sys.path:
#    sys.path.append(os.path.join(os.environ['SOM_ROOT'], 'src'))

from cctbx.sgtbx import space_group, space_group_symbols, \
     space_group_symbol_iterator
from cctbx.uctbx import unit_cell
from iotbx import mtz

if 'XIA2CORE_ROOT' not in os.environ:
    raise RuntimeError('XIA2CORE_ROOT not defined')

sys.path.append(os.path.join(os.environ['XIA2CORE_ROOT'],
                             'Python'))

from Background.Background import Background

from substructure import shelx_cc_weak_pipeline

def guess_nha(cell, pointgroup):
    '''Guess # heavy atoms likely to be in here (as a floating point number)
    based on Matthews coefficient, average proportion of methionine in
    protein sequences and typical mass of an amino acid.'''

    sg = space_group(space_group_symbols(pointgroup).hall())
    uc = unit_cell(cell)

    n_ops = len(sg.all_ops())

    v_asu = uc.volume() / n_ops

    return 0.023 * v_asu / (2.7 * 128)

def nint(a):
    return int(round(a))

def useful_nha(cell, pointgroup):
    nha = guess_nha(cell, pointgroup)

    result = []

    for f in [0.25, 0.5, 1.0, 2.0, 4.0]:
        nha_test = nint(f * nha)
        if nha_test and not nha_test in result:
            result.append(nha_test)

    return result

def generate_enantiomorph_unique_spacegroups(pointgroup):
    '''Generate an enantiomorph unique list of chiral spacegroups which
    share a pointgroup with this pointgroup.'''

    sg = space_group(space_group_symbols(pointgroup).hall())
    pg = sg.build_derived_patterson_group()

    eu_list = []

    for j in space_group_symbol_iterator():
        sg_test = space_group(j)

        if not sg_test.is_chiral():
            continue

        pg_test = sg_test.build_derived_patterson_group()
        if pg_test == pg:
            enantiomorph = sg_test.change_basis(
                sg_test.type().change_of_hand_op())
            if not sg_test in eu_list and not \
               enantiomorph in eu_list:
                eu_list.append(sg_test)

    return [
        sg_test.type().lookup_symbol().replace(' ', '') \
        for sg_test in eu_list]

def generate_all_spacegroups(pointgroup):
    '''Generate an enantiomorph unique list of chiral spacegroups which
    share a pointgroup with this pointgroup.'''

    sg = space_group(space_group_symbols(pointgroup).hall())
    pg = sg.build_derived_patterson_group()

    eu_list = []

    for j in range(1, 231):
        sg_test = space_group(space_group_symbols(j).hall())

        if not sg_test.is_chiral():
            continue

        pg_test = sg_test.build_derived_patterson_group()
        if pg_test == pg:
            if not sg_test in eu_list:
                eu_list.append(sg_test)

    return [
        sg_test.type().universal_hermann_mauguin_symbol().replace(' ', '') \
        for sg_test in eu_list]

def brute_force_substructure(hklin):

    wd = os.getcwd()

    m = mtz.object(hklin)

    pointgroup = m.space_group().type().number()

    for crystal in m.crystals():
        if crystal.name() != 'HKL_base':
            uc = crystal.unit_cell().parameters()

    substructure_pipelines = { }
    jobs = []

    for spacegroup in generate_enantiomorph_unique_spacegroups(pointgroup):
        for nha in useful_nha(uc, pointgroup):

            wd_j = os.path.join(wd, spacegroup, str(nha))

            if not os.path.exists(wd_j):
                os.makedirs(wd_j)

            shelx_pipeline = shelx_cc_weak_pipeline()
            shelx_pipeline.set_working_directory(wd_j)
            shelx_pipeline.set_hklin(hklin)
            shelx_pipeline.set_nha(nha)
            shelx_pipeline.set_symmetry(spacegroup)
            substructure_pipelines[(spacegroup, nha)] = shelx_pipeline

            job = Background(shelx_pipeline, 'shelx_cc_weak_pipeline')
            jobs.append(job)
            job.start()

    for j, job in enumerate(jobs):
        try:
           job.stop()
        except Exception as e:
            print(e)
            print(job.get_traceback())

    best_cc_weak = 0.0
    best_cc = 0.0
    best_spacegroup = None
    best_nha = None

    for spacegroup in generate_enantiomorph_unique_spacegroups(pointgroup):
        for nha in useful_nha(uc, pointgroup):
            cc, cc_weak = substructure_pipelines[(spacegroup, nha)].get_cc()

            if cc_weak is not None and cc_weak > best_cc_weak:
                best_cc_weak = cc_weak
                best_cc = cc
                best_spacegroup = spacegroup
                best_nha = nha


    print('Best solution: %s with %d sites, %.3f / %.3f' % \
          (best_spacegroup, best_nha, best_cc, best_cc_weak))

    return

if __name__ == '__main__':

    brute_force_substructure(os.path.abspath(sys.argv[1]))
