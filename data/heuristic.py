import os
import re
import sys
import time
from pydicom import dcmread


def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


def GE_infotodict(seqinfo):
    info = {t1w_norm: [], t1w_nonnorm: [],
            t2w_norm: [], t2w_nonnorm: [],
            dwi: [], dwi_sbref: [],
            dwi_b0: [], dwi_b0_sbref: [],
            rest_ap: [], rest_pa: [],
            rest_ap_sbref: [], rest_pa_sbref: [],
            fmap: [],
            localizer: [], localizer_aligned: [],
            scout: []}

    for s in seqinfo:
        print('='*80)
        print(s)
        print(s.example_dcm_file_path)
        print('='*80)
        if 't1w' in s.series_description.lower():
            print('='*80)
            print('Here is s variable')
            print(s)
            print('='*80)
            try:
                # JE site uses Siemens XA30, which stores normalization info
                # in one of the private tag
                ds = dcmread(s.example_dcm_file_path)
                t1w_private_tag = ds[0x52009230][0][0x002111fe][0][0x00211175].value
            except:
                t1w_private_tag = ''
            
            print(t1w_private_tag)

            if 'NORM' in s.image_type or 'NORM' in t1w_private_tag:# or 'NORM' in s.ImageTypeText:
                info[t1w_norm].append({'item': s.series_id})
            else:
                info[t1w_nonnorm].append({'item': s.series_id})

        if 't2w' in s.series_description.lower():
            try:
                # JE site uses Siemens XA30, which stores normalization info
                # in one of the private tag
                ds = dcmread(s.example_dcm_file_path)
                t2w_private_tag = ds[0x52009230][0][0x002111fe][0][0x00211175].value
            except:
                t2w_private_tag = ''

            # "ImageTypeText": ["ORIGINAL", "PRIMARY", "M", "NORM", "DIS2D"],
            if 'NORM' in s.image_type or 'NORM' in t2w_private_tag:# or 'NORM' in s.ImageTypeText:
                info[t2w_norm].append({'item': s.series_id})
            else:
                info[t2w_nonnorm].append({'item': s.series_id})

        if 'dmri' in s.series_description.lower():
            print('-'*80)
            print(s)
            print('-'*80)
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
            # if series_num < 10:
            # elif series_num < 20:
                # tmp_dict['acq'] = 'dwi'
            # else:  #series_num < 30:
                # tmp_dict['acq'] = 'fmri'

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
                     'anat/sub-{subject}_{session}_rec-nonnorm_run-{item}_T1w')

    t2w_norm = create_key('sub-{subject}/{session}/'
                     'anat/sub-{subject}_{session}_rec-norm_run-{item}_T2w')

    t2w_nonnorm = create_key('sub-{subject}/{session}/'
                     'anat/sub-{subject}_{session}_rec-nonnorm_run-{item}_T2w')

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

    info = {t1w_norm: [], t1w_nonnorm: [],
            t2w_norm: [], t2w_nonnorm: [],
            dwi: [],
            dwi_sbref: [],
            dwi_b0: [],
            dwi_b0_sbref: [],
            rest_ap: [],
            rest_pa: [],
            rest_ap_sbref: [],
            rest_pa_sbref: [],
            fmap: [],
            localizer: [],
            localizer_aligned: [],
            scout: []}


    for s in seqinfo:
        print('='*80)
        print(s)
        print(s.example_dcm_file_path)
        print('='*80)
        if 't1w' in s.series_description.lower():
            print('='*80)
            print('Here is s variable')
            print(s)
            print('='*80)
            try:
                # JE site uses Siemens XA30, which stores normalization info
                # in one of the private tag
                ds = dcmread(s.example_dcm_file_path)
                t1w_private_tag = ds[0x52009230][0][0x002111fe][0][0x00211175].value
            except:
                t1w_private_tag = ''
            
            print(t1w_private_tag)

            if 'NORM' in s.image_type or 'NORM' in t1w_private_tag:# or 'NORM' in s.ImageTypeText:
                info[t1w_norm].append({'item': s.series_id})
            else:
                info[t1w_nonnorm].append({'item': s.series_id})

        if 't2w' in s.series_description.lower():
            try:
                # JE site uses Siemens XA30, which stores normalization info
                # in one of the private tag
                ds = dcmread(s.example_dcm_file_path)
                t2w_private_tag = ds[0x52009230][0][0x002111fe][0][0x00211175].value
            except:
                t2w_private_tag = ''

            # "ImageTypeText": ["ORIGINAL", "PRIMARY", "M", "NORM", "DIS2D"],
            if 'NORM' in s.image_type or 'NORM' in t2w_private_tag:# or 'NORM' in s.ImageTypeText:
                info[t2w_norm].append({'item': s.series_id})
            else:
                info[t2w_nonnorm].append({'item': s.series_id})

        if 'dmri' in s.series_description.lower():
            print('-'*80)
            print(s)
            print('-'*80)
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
            # if series_num < 10:
            # elif series_num < 20:
                # tmp_dict['acq'] = 'dwi'
            # else:  #series_num < 30:
                # tmp_dict['acq'] = 'fmri'

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
