import os
import re

import sys
import time

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """
    # return info
    t1w = create_key('sub-{subject}/{session}/'
                     'anat/sub-{subject}_ses-{session}_rec-{norm}_T1w')
    t2w = create_key('sub-{subject}/{session}/'
                     'anat/sub-{subject}_ses-{session}_rec-{norm}_T2w')

    # dwi
    dwi = create_key(
            'sub-{subject}/{session}/dwi/'
            'sub-{subject}_ses-{session}_acq-{dirnum}_dir-{APPA}'
            '_dwi')

    dwi_sbref = create_key(
            'sub-{subject}/{session}/dwi/'
            'sub-{subject}_ses-{session}_acq-{dirnum}_dir-{APPA}'
            '_sbref')

    dwi_b0 = create_key(
            'sub-{subject}/{session}/dwi/'
            'sub-{subject}_ses-{session}_acq-b0_dir-{APPA}_run-{item}'
            '_dwi')

    dwi_b0_sbref = create_key(
            'sub-{subject}/{session}/dwi/'
            'sub-{subject}_ses-{session}_acq-b0_dir-{APPA}_run-{item}'
            '_sbref')

    # rest
    rest_ap = create_key(
            'sub-{subject}/{session}/func/'
            'sub-{subject}_ses-{session}_task-rest_dir-AP'
            '_run-{item}_bold')

    rest_pa = create_key(
            'sub-{subject}/{session}/func/'
            'sub-{subject}_ses-{session}_task-rest_dir-PA'
            '_run-{item}_bold')

    rest_ap_sbref = create_key(
            'sub-{subject}/{session}/func/'
            'sub-{subject}_ses-{session}_task-rest_dir-AP'
            '_run-{item}_sbref')

    rest_pa_sbref = create_key(
            'sub-{subject}/{session}/func/'
            'sub-{subject}_ses-{session}_task-rest_dir-PA'
            '_run-{item}_sbref')

    # distortion maps
    fmap = create_key(
            'sub-{subject}/{session}/fmap/'
            'sub-{subject}_ses-{session}_mod-{mod}_dir-{APPA}_epi')

    info = {t1w: [], t2w: [],
            dwi: [],
            dwi_sbref: [],
            dwi_b0: [],
            dwi_b0_sbref: [],
            rest_ap: [],
            rest_pa: [],
            rest_ap_sbref: [],
            rest_pa_sbref: [],
            fmap: []}


    for s in seqinfo:
        if 'T1w' in s.protocol_name:
            if 'NORM' in s.image_type:  # exclude non motion corrected series
                info[t1w].append({'item': s.series_id, 'norm': 'norm'})
            else:
                info[t1w].append({'item': s.series_id, 'norm': 'nonorm'})

        if 'T2w' in s.protocol_name:
            if ('NORM' in s.image_type):  # exclude non motion corrected series
                info[t2w].append({'item': s.series_id, 'norm': 'norm'})
            else:
                info[t2w].append({'item': s.series_id, 'norm': 'nonorm'})

        if 'dMRI' in s.protocol_name:
            if '_dir' in s.series_description:
                sbref = True if 'SBRef' in s.series_description else False
                appa = 'AP' if '_AP' in s.seres_description else 'PA'
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
                sbref = True if 'SBRef' in s.series_description else False
                appa = 'AP' if '_AP' in s.series_description else 'PA'
                if sbref:
                    info[dwi_b0_sbref].append({'item': s.series_id,
                                               'APPA': appa})
                else:
                    info[dwi_b0].append({'item': s.series_id,
                                               'APPA': appa})


        if ('rfMRI' in s.protocol_name):
            sbref = True if 'SBRef' in s.series_description else False
            appa = True if '_AP' in s.series_description else False

            if appa and sbref:
                info[rest_ap_sbref].append({'item': s.series_id})
            elif not appa and sbref:
                info[rest_pa_sbref].append({'item': s.series_id})
            elif appa and not sbref:
                info[rest_ap].append({'item': s.series_id})
            elif not appa and not sbref:
                info[rest_pa].append({'item': s.series_id})


        if ('distortion' in s.series_description.lower()):
            appa = 'AP' if '_AP' in s.series_description else 'PA'
            series_num = int(re.search(r'\d+', s.series_id).group(0))
            tmp_dict = {'item': s.series_id,
                        'APPA': appa,
                        'num': re.search(r'\d+', s.series_id).group(0)}

            if series_num < 10:
                tmp_dict['mod'] = 'anat'
            elif series_num < 20:
                tmp_dict['mod'] = 'dwi'
            else:  #series_num < 30:
                tmp_dict['mod'] = 'fmri'

            info[fmap].append(tmp_dict)


    return info
