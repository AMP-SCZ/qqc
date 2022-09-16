import re
from subprocess import PIPE, Popen
from pathlib import Path
import json
from qqc.qqc.mriqc import remove_DataSetTrailingPadding_from_json_files


def run_fmriprep_on_data(rawdata_dir: Path,
                         subject_id: str,
                         session_id: str,
                         fmriprep_outdir_root: Path,
                         fs_outdir_root: Path,
                         temp_dir: str = '/data/predict/kcho/tmp',
                         bsub: bool = True) -> None:
    '''Run fmriprep following the quick QC

    Key Argument:
        rawdata_dir: root of the BIDS nifti structure
        subject_id: subject ID, including 'sub-'
        session_id: session ID, including 'ses-'
        fmriprep_outdir_root: root of the fmriprep out dir, Path.
        fs_outdir_root: root of the freesurfer out dir, Path.
        temp_dir: location of fmriprep working directory
        bsub: bsub option, bool.
    '''
    # img_loc = '/data/predict/mg1050/singularity_images/fmriprep-20.2.6.sif'
    # img_loc = '/data/predict/kcho/singularity_images/fmriprep-22.0.0rc0.simg'
    # img_loc = '/data/predict/kcho/singularity_images/fmriprep-22.0.0rc2.simg'
    img_loc = '/data/predict/kcho/singularity_images/fmriprep-22.0.0.simg'
    singularity = '/apps/released/gcc-toolchain/gcc-4.x/singularity/' \
                  'singularity-3.7.0/bin/singularity'

    work_dir = Path(temp_dir) / 'fmriprep' / subject_id / session_id
    work_dir.mkdir(exist_ok=True, parents=True)

    remove_DataSetTrailingPadding_from_json_files(
            rawdata_dir, subject_id, session_id)

    for datadir in fmriprep_outdir_root, fs_outdir_root:
        if not datadir.is_dir():
            datadir.mkdir(exist_ok=True, parents=True)

    filter_dict = {"t1w": {"datatype": "anat",
                           "session": session_id.split('-')[1],
                           "suffix": "T1w"},
                   "bold": {"datatype": "func",
                            "session": session_id.split('-')[1],
                            "suffix": "bold"}}

    with open(work_dir / 'filter.json', 'w') as fp:
        json.dump(filter_dict, fp, indent=1)

    command = f'{singularity} run -e \
        -B {rawdata_dir}:/data:ro \
        -B {work_dir}:/work \
        -B {fmriprep_outdir_root}:/out \
        -B {fs_outdir_root}:/fsdir \
        -B /data/pnl/soft/pnlpipe3/freesurfer/license.txt:/opt/freesurfer/license.txt \
        -B {work_dir}/filter.json:/filter.json \
        {img_loc} \
        /data /out participant \
        -w /work --participant-label {subject_id} \
        --nprocs 8 --mem 20G --omp-nthreads 2 \
        --fs-subjects-dir /fsdir \
        --output-layout bids \
        --verbose \
        --skip_bids_validation \
        --notrack \
        --bids-filter-file /filter.json'

    print(command)
    
    if bsub:
        command = f'bsub -q pri_pnl \
                -o {fmriprep_outdir_root}/fmriprep.out \
                -e {fmriprep_outdir_root}/fmriprep.err \
                -n 8 -J fmriprep_{subject_id}_{session_id} \
                {command}'

    command = re.sub(r'\s+', ' ', command)
    print(command)

    p = Popen(command, shell=True, stdout=PIPE, bufsize=1)
    for line in iter(p.stdout.readline, b''):
        print(line)
    p.stdout.close()
    p.wait()
