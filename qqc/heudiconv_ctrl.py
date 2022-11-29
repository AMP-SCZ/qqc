import qqc
import os
import subprocess
import logging
from pathlib import Path
logger = logging.getLogger(__name__)
from typing import Union


def run_heudiconv(dicom_input_root: Union[Path, str],
                  subject_name: str,
                  session_name: str,
                  nifti_root_dir:Union[Path, str],
                  qc_out_dir: Path) -> None:
    '''Run heudiconv on specified subjects to create nifti structure in BIDS
    
    Key Arguments:
        dicom_input_root: root of dicom directory, where there should be
                          {subject}/{session} directories, Path or str.
                          eg. /data/predict/phantom_human_pilot/sourcedata
                              └── ProNET_UCLA
                                  ├── ses-humanpilot
                                  └── ses-phantom
        subject_name: Name of subject, str.
                      eg) ProNET_UCLA
        session_name: Name of session str. Must not have "ses" in front.
                      eg) humanpilot
        nifti_root_dir: root of the nifti output, Path or str.
        qc_out_dir: QC out directory, Path.

    Returns:
        None

    Note:
        - Heudiconv will use the "qqc/data/heuristic.py"
    '''
    data_dir = Path(qqc.__file__).parent.parent / 'data'
    heuristic_file =  data_dir / 'heuristic.py'
    # heuristic_file = data_dir / 'dpacc-heuristic.py'

    # os.environ['dcm2niix'] = \
            # '/data/predict/phantom_data/softwares' \
            # '/newest_dcm2niix_2022/dcm2niix'

    # os.environ['dcm2niix'] = \
            # '/data/predict/phantom_data/softwares/dcm2niix/dcm2niix'

    # os.environ['dcm2niix'] = \
            # '/data/predict/phantom_data/kcho/devel_soft/'\
            # 'dcm2niix_devel_branch/dcm2niix/build/bin/dcm2niix'
# /data/predict/phantom_data/softwares/dcm2niix_bb3a6c3/build/bin/dcm2niix
    os.environ['dcm2niix'] = \
            '/data/predict/phantom_data/softwares/dcm2niix_bb3a6c3/' \
            'build/bin/dcm2niix'

    # os.environ['dcm2niix'] = \
            # '/data/predict/phantom_data/softwares/dcm2niix_2a9fbe8/' \
            # 'build/bin/dcm2niix'

    command = f'heudiconv \
        -d {dicom_input_root}' + '/{subject}/ses-{session}/*/* ' \
        f'-f {heuristic_file} ' \
        f'-s {subject_name} -ss {session_name} -c dcm2niix \
        --overwrite \
        -b \
        -o {nifti_root_dir}'

    logger.info('Running heudiconv')
    logger.info('heudiconv command: %s' % command)
    print(os.popen(command).read())

    # try:
        # proc = subprocess.check_output(command, stderr=subprocess.STDOUT)
    # except subprocess.CalledProcessError:
        # logger.error('heudiconv fails')
        # send_error(f'QQC - heudiconv failure {subject_name} {session_name}',
                   # 'Heudiconv failure',
                   # 'dicom input root: {dicom_input_root}',
                   # proc)

    # with open(qc_out_dir / '99_heudiconv_log.txt', 'a') as fp:
        # fp.write(proc)
