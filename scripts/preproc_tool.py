import sys
from pathlib import Path
from qqc.qqc.mriqc import run_mriqc_on_data
from qqc.qqc.fmriprep import run_fmriprep_on_data
from qqc.qqc.dwipreproc import run_quick_dwi_preproc_on_data
import argparse
from argparse import RawTextHelpFormatter


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
        description='''Convert dicoms to BIDS

    preproc_tool.py \\
        --subject_name Pronet_PNL \\
        --session_name humanpilot \\
        --output_dir ${bids_out_dir} \\
        --mriqc --fmriprep --dwipreproc \\


    python preproc_tool.py \\
        --output_dir /data/predict/data_from_nda/MRI_ROOT \\
        -s sub-ME0106 -ss ses-202209091 \\
        --mriqc --fmriprep --dwipreproc''',
        formatter_class=RawTextHelpFormatter)

    # image input related options
    parser.add_argument('--subject_name', '-s', type=str,
                        help='Subject name.')

    parser.add_argument('--session_name', '-ss', type=str,
                        help='Session name.')

    parser.add_argument('--output_dir', '-o', type=str,
                        help='BIDS Output directory')

    parser.add_argument('--mriqc', '-mriqc', action='store_true',
                        help='Run MRIQC following conversion')

    parser.add_argument('--fmriprep', '-fmriprep', action='store_true',
                        help='Run FMRIPREP following conversion')

    parser.add_argument('--dwipreproc', '-dwipreproc', action='store_true',
                        help='Run DWI preprocessing following conversion')

    parser.add_argument('--nobsub', action='store_true',
                        help='Run DWI preprocessing following conversion')

    # extra options
    args = parser.parse_args(argv)

    return args

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    output_dir = Path(args.output_dir)
    deriv_p = output_dir / 'derivatives'
    subject_name = args.subject_name
    session_name = args.session_name

    if args.dwipreproc:
        # quick dwi preprocessing
        dwipreproc_outdir_root = deriv_p / 'dwipreproc'
        if args.nobsub:
            bsub = False
        else:
            bsub = True
        run_quick_dwi_preproc_on_data(
            output_dir / 'rawdata',
            subject_name,
            session_name,
            dwipreproc_outdir_root,
            bsub)

    if args.mriqc:
        # mriqc
        mriqc_outdir_root = deriv_p / 'mriqc'
        run_mriqc_on_data(
            output_dir / 'rawdata',
            subject_name,
            session_name,
            mriqc_outdir_root)

    if args.fmriprep:
        # fmriprep
        fmriprep_outdir_root = deriv_p / 'fmriprep'
        fs_outdir_root = deriv_p / 'freesurfer'
        run_fmriprep_on_data(
            output_dir / 'rawdata',
            subject_name,
            session_name,
            fmriprep_outdir_root,
            fs_outdir_root)
