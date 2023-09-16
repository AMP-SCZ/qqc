import re
from subprocess import PIPE, Popen
from pathlib import Path
import json
import os


def remove_DataSetTrailingPadding_from_json_files(
        rawdata_dir: Path,
        subject_id: str,
        session_id: str) -> None:
    '''Remove DataSetTrailingPadding from the existing json files'''
    session_path = rawdata_dir / subject_id / session_id
    json_files = list(Path(session_path).glob('*/*json'))
    for json_file in json_files:
        with open(json_file, 'r') as fp:
            data = json.load(fp)
        if 'global' in data.keys():
            # anat
            if 'DataSetTrailingPadding' in data['global']['slices'].keys():
                data['global']['slices']['DataSetTrailingPadding'] = 'removed'
                os.chmod(json_file, 0o744)
                with open(json_file, 'w') as fp:
                    json.dump(data, fp, indent=1)
                os.chmod(json_file, 0o444)

        if 'time' in data.keys():
            # fmri
            if 'DataSetTrailingPadding' in data['time']['samples'].keys():
                data['time']['samples']['DataSetTrailingPadding'] = 'removed'
                os.chmod(json_file, 0o744)
                with open(json_file, 'w') as fp:
                    json.dump(data, fp, indent=1)
                os.chmod(json_file, 0o444)


def run_mriqc_on_data(rawdata_dir: Path,
                      subject_id: str,
                      session_id: str,
                      mriqc_outdir_root: Path,
                      temp_dir: str = '/data/predict1/home/kcho/tmp',
                      bsub: bool = True,
                      specific_nodes: list = []) -> None:
    '''Run MRI-QC following the quick QC

    Key Argument:
        rawdata_dir: root of the BIDS nifti structure
        subject_id: subject ID, including 'sub-'
        session_id: session ID, including 'ses-'
        mriqc_outdir_root: root of the MRIQC out dir, Path.
        temp_dir: location of mriqc working directory
        bsub: bsub option, bool.
    '''
    img_loc = '/data/predict1/home/kcho/singularity_images/mriqc-22.0.6.simg'
    singularity = '/apps/released/gcc-toolchain/gcc-4.x/singularity/' \
                  'singularity-3.7.0/bin/singularity'

    work_dir = Path(temp_dir) / 'mriqc' / subject_id / session_id
    work_dir.mkdir(exist_ok=True, parents=True)
    mriqc_outdir_root.mkdir(exist_ok=True, parents=True)

    remove_DataSetTrailingPadding_from_json_files(
            rawdata_dir, subject_id, session_id)

    command = f'{singularity} run -e \
        -B {rawdata_dir}:/data:ro \
        -B {work_dir}:/work \
        -B {mriqc_outdir_root}:/out \
        -B /data/pnl/soft/pnlpipe3/freesurfer/license.txt:/opt/freesurfer/license.txt \
        {img_loc} \
        /data /out participant \
        -w /work --participant-label {subject_id} \
        --session-id {session_id.split("-")[1]} \
        --nprocs 1 --mem 16G --omp-nthreads 1 \
        --no-sub \
        --verbose-reports'

    if bsub:
        if specific_nodes == []:
            command = f'bsub -q pri_pnl \
                    -o {mriqc_outdir_root}/mriqc.out \
                    -e {mriqc_outdir_root}/mriqc.err \
                    -n 1 -J mriqc_{subject_id}_{session_id} \
                    {command}'
        else:
            nodes = ' '.join(specific_nodes)
            command = f'bsub -q pri_pnl \
                    -o {mriqc_outdir_root}/mriqc.out \
                    -e {mriqc_outdir_root}/mriqc.err \
                    -m "{nodes}" \
                    -n 1 -J mriqc_{subject_id}_{session_id} \
                    {command}'

    command = re.sub('\s+', ' ', command)
    print(command)

    p = Popen(command, shell=True, stdout=PIPE, bufsize=1)
    for line in iter(p.stdout.readline, b''):
        print(line)
    p.stdout.close()
    p.wait()
