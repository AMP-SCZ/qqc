import os
import re
import sys
import time
import json
from pydicom import dcmread


def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


def print_missing_message(modality, s):
    print('-'*80)
    print(f'There might be missing files in {modality}')
    print('Please check the number of dicom files, and try '
          'running dcm2niix separately. If the dcm2niix works '
          'fine on the dicoms, please update the number of '
          'expected dicom file number in the heuristic file')
    print(s)
    print('-'*80)


def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group

    """

    localizer = create_key(
            'sub-{subject}/{session}/ignore/'
            'sub-{subject}_{session}_ignore-bids_num-{num}_localizer')

    localizer_aligned = create_key(
            'sub-{subject}/{session}/ignore/'
            'sub-{subject}_{session}_ignore-bids_num-{num}_localizer_aligned')

    scout = create_key(
            'sub-{subject}/{session}/ignore/'
            'sub-{subject}_{session}_ignore-bids_num-{num}_scout')

    # return info
    t1w_norm = create_key('sub-{subject}/{session}/'
                     'anat/sub-{subject}_{session}_rec-norm_run-{item}_T1w')

    t1w_nonnorm = create_key('sub-{subject}/{session}/'
         'anat/sub-{subject}_{session}_rec-nonnorm_run-{item}_T1w_auxiliary')

    t1w = create_key('sub-{subject}/{session}/'
                     'anat/sub-{subject}_{session}_run-{item}_T1w')

    t1w_axil = create_key('sub-{subject}/{session}/'
         'anat/sub-{subject}_{session}_run-{item}_T1w_auxiliary')

    t2w_norm = create_key('sub-{subject}/{session}/'
         'anat/sub-{subject}_{session}_rec-norm_run-{item}_T2w')

    t2w_nonnorm = create_key('sub-{subject}/{session}/'
         'anat/sub-{subject}_{session}_rec-nonnorm_run-{item}_T2w_auxiliary')

    t2w = create_key('sub-{subject}/{session}/'
                     'anat/sub-{subject}_{session}_run-{item}_T2w')

    t2w_axil = create_key('sub-{subject}/{session}/'
         'anat/sub-{subject}_{session}_run-{item}_T2w_auxiliary')

    # dwi
    dwi = create_key(
            'sub-{subject}/{session}/dwi/'
            'sub-{subject}_{session}_acq-{dirnum}_dir-{APPA}_run-{item}'
            '_dwi')

    dwi_sbref = create_key(
            'sub-{subject}/{session}/dwi/'
            'sub-{subject}_{session}_acq-{dirnum}_dir-{APPA}_run-{item}'
            '_sbref')

    dwi_b0 = create_key(
            'sub-{subject}/{session}/dwi/'
            'sub-{subject}_{session}_acq-b0_dir-{APPA}_run-{item}'
            '_dwi')

    dwi_b0_sbref = create_key(
            'sub-{subject}/{session}/dwi/'
            'sub-{subject}_{session}_acq-b0_dir-{APPA}_run-{item}'
            '_sbref')

    dwi_fa = create_key(
            'sub-{subject}/{session}/dwi/'
            'sub-{subject}_{session}_acq-{dirnum}_dir-{APPA}_run-{item}'
            '_fa')

    dwi_colfa = create_key(
            'sub-{subject}/{session}/dwi/'
            'sub-{subject}_{session}_acq-{dirnum}_dir-{APPA}_run-{item}'
            '_fa')

    # rest
    rest_ap = create_key(
            'sub-{subject}/{session}/func/'
            'sub-{subject}_{session}_task-rest_dir-AP'
            '_run-{item}_bold')

    rest_pa = create_key(
            'sub-{subject}/{session}/func/'
            'sub-{subject}_{session}_task-rest_dir-PA'
            '_run-{item}_bold')

    rest_ap_sbref = create_key(
            'sub-{subject}/{session}/func/'
            'sub-{subject}_{session}_task-rest_dir-AP'
            '_run-{item}_sbref')

    rest_pa_sbref = create_key(
            'sub-{subject}/{session}/func/'
            'sub-{subject}_{session}_task-rest_dir-PA'
            '_run-{item}_sbref')

    # distortion maps
    fmap = create_key(
            'sub-{subject}/{session}/fmap/'
            'sub-{subject}_{session}_acq-{acq}_dir-{APPA}_run-{item}_epi')

    info = {t1w_norm: [], t1w_nonnorm: [], t1w: [], t1w_axil: [],
            t2w_norm: [], t2w_nonnorm: [], t2w: [], t2w_axil: [],
            dwi: [],
            dwi_sbref: [],
            dwi_b0: [],
            dwi_b0_sbref: [],
            dwi_colfa: [], dwi_fa: [],
            rest_ap: [],
            rest_pa: [],
            rest_ap_sbref: [],
            rest_pa_sbref: [],
            fmap: [],
            localizer: [],
            localizer_aligned: [],
            scout: []}

        # 'ge_machine': {
                # 't1w': 208, 't2w': 204,
                # 'distortion': 132,
                # 'rest_sbref': 132,
                # 'rest': 22308,
                # 'b0': 729,
                # 'dMRI':10368},
    count_infos = {
        'ge_machine': {
                't1w': 208, 't2w': 204,
                'distortion': 132,
                'rest_sbref': 132,
                'rest': 22308,
                'b0': 594,
                'dMRI':8448},
        'xa30': {
                't1w': 208, 't2w': 208,
                'distortion': 1,
                'rest_sbref': 1,
                'rest': 333,
                'b0': 7,
                'dMRI':117},
        'philips': {
                't1w': 208, 't2w': 208,
                'distortion': 67,
                'rest_sbref': 133,
                'rest': 22639,
                'b0': 568,
                'dMRI':10288},
        'prisma': {
                't1w': 1, 't2w': 1,
                'distortion': 1,
                'rest_sbref': 1,
                'rest': 333,
                'b0': 7,
                'dMRI':177},
        'vida': {
                't1w': 1, 't2w': 1,
                'distortion': 1,
                'rest_sbref': 1,
                'rest': 333,
                'b0': 7,
                'dMRI': 127},
        'skyra': {
                't1w': 1, 't2w': 1,
                'distortion': 1,
                'rest_sbref': 1,
                'rest': 333,
                'b0': 7,
                'dMRI': 127},
            }

    # check machine and software versions
    for s in seqinfo:
        try:
            ds = dcmread(s.example_dcm_file_path)
            sv = str(ds.SoftwareVersions)
            machine = str(ds.Manufacturer)
            machine_model = str(ds.ManufacturerModelName)
            xa30 = True if 'xa30' in sv.lower() else False
            xa31 = True if 'xa31' in sv.lower() else False
            xa50 = True if 'xa50' in sv.lower() else False
            ge_machine = True if 'ge' in machine.lower() else False
            philips_machine = True if 'philips' in machine.lower() else False
            vida_machine = True if 'vida' in machine_model.lower() else False
            skyra_machine = True if 'skyra' in machine_model.lower() else False
            print(f'Is it XA30: {xa30}')
            print(f'Is it GE: {ge_machine}')
            print(f'Is it Philips: {philips_machine}')
            print(f'Is it Vida: {vida_machine}')
            print(f'Is it Skyra: {vida_machine}')
            break
        except AttributeError:
            pass

    if ge_machine:
        count_info = count_infos['ge_machine']
    elif philips_machine:
        count_info = count_infos['philips']
    elif vida_machine:
        count_info = count_infos['vida']
    elif skyra_machine:
        count_info = count_infos['skyra']
    else:
        count_info = count_infos['prisma']

    for s in seqinfo:
        if 't1w' in s.series_description.lower():
            if s.series_files < count_info['t1w']:
                print_missing_message('t1w', s)
                continue

            # remove adj from converting
            if 'adj' in s.series_description.lower():
                print_missing_message('t1w', s)
                continue

            # XA30
            if xa30 or xa31 or xa50:
                if 't1w_mpr_nd' in s.series_description.lower():
                    info[t1w].append({'item': s.series_id})
                else:
                    info[t1w_axil].append({'item': s.series_id})
            elif ge_machine:
                if 'orig' in s.series_description.lower():
                    info[t1w_axil].append({'item': s.series_id})
                else:
                    info[t1w].append({'item': s.series_id})
            elif philips_machine:
                info[t1w].append({'item': s.series_id})
                continue
            else:
                if 'NORM' in s.image_type:
                    info[t1w_norm].append({'item': s.series_id})
                else:
                    info[t1w_nonnorm].append({'item': s.series_id})

            continue

        if 't2w' in s.series_description.lower():
            if s.series_files < count_info['t2w']:
                print_missing_message('t2w', s)
                continue

            # remove adj from converting
            if 'adj' in s.series_description.lower():
                print_missing_message('t2w', s)
                continue

            # XA30
            if xa30 or xa31 or xa50:
                if 't2w_spc_nd' in s.series_description.lower():
                    info[t2w].append({'item': s.series_id})
                else:
                    info[t2w_axil].append({'item': s.series_id})
            elif ge_machine:
                if 'orig' in s.series_description.lower():
                    info[t2w_axil].append({'item': s.series_id})
                else:
                    info[t2w].append({'item': s.series_id})
            elif philips_machine:
                info[t2w].append({'item': s.series_id})
                continue
            else:
                if 'NORM' in s.image_type:
                    info[t2w_norm].append({'item': s.series_id})
                else:
                    info[t2w_nonnorm].append({'item': s.series_id})

            continue

        if 'dmri' in s.series_description.lower():
            dirnum = re.search(r'\d+', s.series_description).group(0)
            if '_fa' in s.series_description.lower():
                info[dwi_fa].append({
                    'item': s.series_id, 'dirnum': dirnum,
                    'APPA': appa})
                continue

            if '_colfa' in s.series_description.lower():
                info[dwi_colfa].append({
                    'item': s.series_id, 'dirnum': dirnum,
                    'APPA': appa})
                continue

            if '_dir' in s.series_description.lower():
                sbref = True if 'sbref' in s.series_description.lower() else False
                appa = 'AP' if '_ap' in s.series_description.lower() else 'PA'
                dirnum = re.search(r'\d+', s.series_description).group(0)
                if sbref:
                    info[dwi_sbref].append({
                        'item': s.series_id, 'dirnum': dirnum,
                        'APPA': appa})
                else:
                    if s.series_files < count_info['dMRI']:
                        print_missing_message('dMRI', s)
                        continue
                    info[dwi].append({
                        'item': s.series_id, 'dirnum': dirnum,
                        'APPA': appa})
            else:
                sbref = True if 'sbref' in s.series_description.lower() else False
                appa = 'AP' if '_ap' in s.series_description.lower() else 'PA'
                if sbref:
                    info[dwi_b0_sbref].append({'item': s.series_id,
                                               'APPA': appa})
                else:
                    if s.series_files < count_info['b0']:
                        print_missing_message('b0', s)
                        continue
                    info[dwi_b0].append({'item': s.series_id,
                                               'APPA': appa})
            continue

        if 'rfmri' in s.series_description.lower():
            sbref = True if 'ref' in s.series_description.lower() else False
            appa = True if '_ap' in s.series_description.lower() else False

            if sbref:
                if s.series_files < count_info['rest_sbref']:
                    print_missing_message('rest_sbref', s)
                    continue

                if appa:
                    info[rest_ap_sbref].append({'item': s.series_id})
                else:
                    info[rest_pa_sbref].append({'item': s.series_id})
            else:
                if s.series_files < count_info['rest']:
                    print_missing_message('rest', s)
                    continue
                if appa:
                    info[rest_ap].append({'item': s.series_id})
                else:
                    info[rest_pa].append({'item': s.series_id})

        if 'distortion' in s.series_description.lower():
            if s.series_files < count_info['distortion']:
                print_missing_message('distortion', s)
                continue

            appa = 'AP' if '_ap' in s.series_description.lower() else 'PA'
            series_num = int(re.search(r'\d+', s.series_id).group(0))
            tmp_dict = {'item': s.series_id,
                        'APPA': appa,
                        'num': re.search(r'\d+', s.series_id).group(0)}

            tmp_dict['acq'] = series_num
            info[fmap].append(tmp_dict)


        if 'localizer' in s.series_description.lower() or \
           'calibration' in s.series_description.lower():
            if 'aligned' in s.series_description.lower():
                tmp_dict = {'item': s.series_id,
                            'num': re.search(r'\d+', s.series_id).group(0)}
                info[localizer_aligned].append(tmp_dict)
            else:
                tmp_dict = {'item': s.series_id,
                            'num': re.search(r'\d+', s.series_id).group(0)}
                info[localizer].append(tmp_dict)


        if 'scout' in s.series_description.lower() or \
                'plane_loc' in s.series_description.lower():
            tmp_dict = {'item': s.series_id,
                        'num': re.search(r'\d+', s.series_id).group(0)}
            info[scout].append(tmp_dict)


    return info
