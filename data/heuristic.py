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


# def GE_infotodict(seqinfo):
    # info = {t1w_norm: [], t1w_nonnorm: [],
            # t2w_norm: [], t2w_nonnorm: [],
            # dwi: [], dwi_sbref: [],
            # dwi_b0: [], dwi_b0_sbref: [],
            # rest_ap: [], rest_pa: [],
            # rest_ap_sbref: [], rest_pa_sbref: [],
            # fmap: [],
            # localizer: [], localizer_aligned: [],
            # scout: []}

    # for s in seqinfo:
        # print('='*80)
        # print(s)
        # print(s.example_dcm_file_path)
        # print('='*80)
        # if 't1w' in s.series_description.lower():
            # print('='*80)
            # print('Here is s variable')
            # print(s)
            # print('='*80)
            # try:
                # # Siemens XA30, which stores normalization info
                # # in one of the private tag
                # ds = dcmread(s.example_dcm_file_path)
                # t1w_private_tag = ds[0x52009230][0][0x002111fe][0][0x00211175].value
            # except:
                # t1w_private_tag = ''
            
            # print(t1w_private_tag)

            # if 'NORM' in s.image_type or 'NORM' in t1w_private_tag:# or 'NORM' in s.ImageTypeText:
                # info[t1w_norm].append({'item': s.series_id})
            # else:
                # info[t1w_nonnorm].append({'item': s.series_id})

        # if 't2w' in s.series_description.lower():
            # try:
                # # JE site uses Siemens XA30, which stores normalization info
                # # in one of the private tag
                # ds = dcmread(s.example_dcm_file_path)
                # t2w_private_tag = ds[0x52009230][0][0x002111fe][0][0x00211175].value
            # except:
                # t2w_private_tag = ''

            # # "ImageTypeText": ["ORIGINAL", "PRIMARY", "M", "NORM", "DIS2D"],
            # if 'NORM' in s.image_type or 'NORM' in t2w_private_tag:# or 'NORM' in s.ImageTypeText:
                # info[t2w_norm].append({'item': s.series_id})
            # else:
                # info[t2w_nonnorm].append({'item': s.series_id})

        # if 'dmri' in s.series_description.lower():
            # print('-'*80)
            # print(s)
            # print('-'*80)
            # if '_dir' in s.series_description.lower():
                # sbref = True if 'sbref' in s.series_description.lower() else False
                # appa = 'AP' if '_ap' in s.series_description.lower() else 'PA'
                # dirnum = re.search(r'\d+', s.series_description).group(0)
                # if sbref:
                    # info[dwi_sbref].append({
                        # 'item': s.series_id, 'dirnum': dirnum,
                        # 'APPA': appa})
                # else:
                    # info[dwi].append({
                        # 'item': s.series_id, 'dirnum': dirnum,
                        # 'APPA': appa})
            # else:
                # sbref = True if 'sbref' in s.series_description.lower() else False
                # appa = 'AP' if '_ap' in s.series_description.lower() else 'PA'
                # if sbref:
                    # info[dwi_b0_sbref].append({'item': s.series_id,
                                               # 'APPA': appa})
                # else:
                    # info[dwi_b0].append({'item': s.series_id,
                                               # 'APPA': appa})

        # if 'rfmri' in s.series_description.lower():
            # sbref = True if 'sbref' in s.series_description.lower() else False
            # appa = True if '_ap' in s.series_description.lower() else False

            # if appa and sbref:
                # info[rest_ap_sbref].append({'item': s.series_id})
            # elif not appa and sbref:
                # info[rest_pa_sbref].append({'item': s.series_id})
            # elif appa and not sbref:
                # info[rest_ap].append({'item': s.series_id})
            # elif not appa and not sbref:
                # info[rest_pa].append({'item': s.series_id})

        # if 'distortion' in s.series_description.lower():
            # appa = 'AP' if '_ap' in s.series_description.lower() else 'PA'
            # series_num = int(re.search(r'\d+', s.series_id).group(0))
            # tmp_dict = {'item': s.series_id,
                        # 'APPA': appa,
                        # 'num': re.search(r'\d+', s.series_id).group(0)}

            # tmp_dict['acq'] = series_num
            # # if series_num < 10:
            # # elif series_num < 20:
                # # tmp_dict['acq'] = 'dwi'
            # # else:  #series_num < 30:
                # # tmp_dict['acq'] = 'fmri'

            # info[fmap].append(tmp_dict)

        # if 'localizer' in s.series_description.lower() or \
           # 'calibration' in s.series_description.lower():
            # if 'aligned' in s.series_description.lower():
                # tmp_dict = {'item': s.series_id,
                            # 'num': re.search(r'\d+', s.series_id).group(0)}
                # info[localizer_aligned].append(tmp_dict)
            # else:
                # tmp_dict = {'item': s.series_id,
                            # 'num': re.search(r'\d+', s.series_id).group(0)}
                # info[localizer].append(tmp_dict)

        # if 'scout' in s.series_description.lower() or \
                # 'plane_loc' in s.series_description.lower():
            # tmp_dict = {'item': s.series_id,
                        # 'num': re.search(r'\d+', s.series_id).group(0)}
            # info[scout].append(tmp_dict)

    # return info


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

    # check machine and software versions
    for s in seqinfo:
        try:
            ds = dcmread(s.example_dcm_file_path)
            sv = str(ds.SoftwareVersions)
            xa30 = True if 'xa30' in sv.lower() else False
            xa31 = True if 'xa31' in sv.lower() else False
            ge_machine = True if 'ge' in sv.lower() else False
            print(f'Is it XA30: {xa30}')
            print(f'Is it GE: {ge_machine}')
            break
        except AttributeError:
            pass

    for s in seqinfo:
        if 't1w' in s.series_description.lower():
            # XA30
            if xa30 or xa31:
                if 't1w_mpr_nd' in s.series_description.lower():
                    # Siemens XA30 has no 'NORM' in ImageType, but stores
                    # the norm label in one of the private tag.
                    # ds = dcmread(s.example_dcm_file_path)
                    # private_tag = ds[0x52009230][0]
                    # private_tag_json = private_tag.to_json()

                    # # check if the private tag has both ND and NORM
                    # assert re.search('\"NORM\"', private_tag_json) and \
                        # re.search('\"ND\"', private_tag_json)
                    info[t1w].append({'item': s.series_id})
                else:
                    info[t1w_axil].append({'item': s.series_id})
            elif ge_machine:
                if 'orig' in s.series_description.lower():
                    info[t1w_axil].append({'item': s.series_id})
                else:
                    info[t1w].append({'item': s.series_id})
            else:
                if 'NORM' in s.image_type:
                    info[t1w_norm].append({'item': s.series_id})
                else:
                    info[t1w_nonnorm].append({'item': s.series_id})

            continue

        if 't2w' in s.series_description.lower():
            # XA30
            if xa30 or xa31:
                if 't2w_spc_nd' in s.series_description.lower():
                    # Siemens XA30 has no 'NORM' in ImageType, but stores
                    # the norm label in one of the private tag.
                    # ds = dcmread(s.example_dcm_file_path)
                    # private_tag = ds[0x52009230][0]
                    # private_tag_json = private_tag.to_json()

                    # # check if the private tag has both ND and NORM
                    # assert re.search('\"NORM\"', private_tag_json) and \
                        # re.search('\"ND\"', private_tag_json)
                    info[t2w].append({'item': s.series_id})
                else:
                    info[t2w_axil].append({'item': s.series_id})
            elif ge_machine:
                if 'orig' in s.series_description.lower():
                    info[t2w_axil].append({'item': s.series_id})
                else:
                    info[t2w].append({'item': s.series_id})
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
                    info[dwi_b0].append({'item': s.series_id,
                                               'APPA': appa})
            continue

        if 'rfmri' in s.series_description.lower():
            sbref = True if 'sbref' in s.series_description.lower() else False
            appa = True if '_ap' in s.series_description.lower() else False

            if appa and sbref:
                info[rest_ap_sbref].append({'item': s.series_id})
            elif not appa and sbref:
                info[rest_pa_sbref].append({'item': s.series_id})
            elif appa and not sbref:
                info[rest_ap].append({'item': s.series_id})
            elif not appa and not sbref:
                info[rest_pa].append({'item': s.series_id})

        if 'distortion' in s.series_description.lower():
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
