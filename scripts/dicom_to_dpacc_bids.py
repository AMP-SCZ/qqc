#!/data/pnl/kcho/anaconda3/bin/python
import argparse
import sys
import getpass
import logging
from argparse import RawTextHelpFormatter
from phantom_check.pipeline import dicom_to_bids_QQC

logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler())


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
        description='''Convert dicoms to BIDS

    dicom_to_dpacc_bids.py \\
        --input ${raw_dicom_dir}/human_pilot/data/dicom \\
        --subject_name Pronet_PNL \\
        --session_name humanpilot \\
        --output_dir ${bids_out_dir} \\
        --standard_dir ${bids_out_dir}/rawdata/sub-standard/ses-humanpilot''',
        formatter_class=RawTextHelpFormatter)

    # image input related options
    parser.add_argument('--input', '-i', type=str,
                        help='Raw dicom root directory or zip file.')

    parser.add_argument('--dpacc_input', '-di', type=str,
                        help='Raw dicom root directory.')

    parser.add_argument('--subject_name', '-s', type=str,
                        help='Subject name.')

    parser.add_argument('--session_name', '-ss', type=str,
                        help='Session name.')

    parser.add_argument('--output_dir', '-o', type=str,
                        help='BIDS Output directory')

    parser.add_argument('--qc_subdir', '-qs', type=str,
                        help='ExtraQC output directory name.')

    parser.add_argument('--standard_dir', '-std', type=str,
                        default='/data/predict/phantom_human_pilot/rawdata/'
                                'sub-ProNETUCLA/ses-humanpilot',
                        help='Root of a standard dataset to compare to')

    parser.add_argument('--mriqc', '-mriqc', action='store_true',
                        help='Run MRIQC following conversion')

    parser.add_argument('--fmriprep', '-fmriprep', action='store_true',
                        help='Run FMRIPREP following conversion')

    parser.add_argument('--dwipreproc', '-dwipreproc', action='store_true',
                        help='Run DWI preprocessing following conversion')

    parser.add_argument('--nifti_dir', '-nd', type=str, default=False,
                        help='Nifti root directory. If --nifti_dir is given, '
                             '--input will be ignored and dcm2niix will '
                             'not be ran.')

    parser.add_argument('--skip_dicom_rearrange', '-sdr',
                        action='store_true', default=False,
                        help='Skip dicom rearrange step.')

    parser.add_argument('--skip_heudiconv', '-sh', default=False,
                        action='store_true',
                        help='Skip heudiconv step.')

    parser.add_argument('--skip_qc', '-sq', default=False,
                        action='store_true',
                        help='Skip quick QC step.')
    # extra options
    args = parser.parse_args(argv)
    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    logging.basicConfig(
        filename=args.output_dir + '/dicom_to_dpacc_bids.log',
        format=f'%(asctime):: {getpass.getuser()}:: %(name)s :: '
               '%(levelname)s :: %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG)

    # build up input command to include in the log
    logger.info('*'*80)
    args_reconstruct = ''
    for d in [x for x in dir(args) if not x.startswith('_')]:
        args_reconstruct += f' --{d}={getattr(args, d)}'
    logger.info(f'command used: \ndicom_to_dpacc_bids.py {args_reconstruct}')
    logger.info('Dicom to DPACC BIDS conversion started')
    dicom_to_bids_QQC(args)
    logger.info('Completed')

