import re
import os
from subprocess import PIPE, Popen
from pathlib import Path


def run_quick_dwi_preproc_on_data(rawdata_dir: Path,
                                  subject_id: str,
                                  session_id: str,
                                  dwipreproc_outdir_root: Path,
                                  bsub: bool = True) -> None:
    '''Run quick DWI preprocessing following the quick QC

    Key Argument:
        rawdata_dir: root of the BIDS nifti structure
        subject_id: subject ID, including 'sub-'
        session_id: session ID, including 'ses-'
        mriqc_outdir_root: root of the MRIQC out dir, Path.
        temp_dir: location of mriqc working directory
        bsub: bsub option, bool.
    '''

    bids_dwi_nifti_root = rawdata_dir / subject_id / session_id / 'dwi'

    dwipreproc_bash_code = Path(os.path.realpath(__file__)).parent / \
                           'dwipreproc.sh'
    dwipreproc_python_code = '/data/predict/kcho/ampscz_mri/scripts/' \
                             'run_ampscz_mri_pipe.py'

    command = f'python {dwipreproc_python_code} \
            --mri_root {rawdata_dir.parent} \
            --ampscz_id {subject_id} --session {session_id}'
    
    if bsub:
        command = f'bsub -q pri_pnl \
                -o {dwipreproc_outdir_root}/dwipreproc.out \
                -e {dwipreproc_outdir_root}/dwipreproc.err \
                -n 8 -J dwipreproc_{subject_id}_{session_id} \
                {command}'

    command = re.sub('\s+', ' ', command)
    print(command)

    p = Popen(command, shell=True, stdout=PIPE, bufsize=1)
    for line in iter(p.stdout.readline, b''):
        print(line)
    p.stdout.close()
    p.wait()
