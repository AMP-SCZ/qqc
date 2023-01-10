#!/data/pnl/kcho/anaconda3/bin/python
import argparse
import configparser
import sys
import getpass
import logging
from argparse import RawTextHelpFormatter
from qqc.pipeline import dicom_to_bids_QQC
from pathlib import Path
import re
sys.path.append('/data/predict/phantom_data/kcho/devel_soft/qqc')

logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler())


def get_standard_dir(site: str) -> str:
    '''pass'''
    config = configparser.RawConfigParser()
    config.read('/data/predict/data_from_nda/MRI_ROOT/standard_templates.cfg')


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
        description='''Convert dicoms to BIDS

    dicom_to_dpacc_bids.py \\
        --input ${raw_dicom_dir}/human_pilot/data/dicom \\
        --subject_name Pronet_PNL \\
        --session_name humanpilot \\
        --bids_root ${bids_out_dir} \\
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

    parser.add_argument('--bids_root', '-o', type=str,
                        help='BIDS Output directory')

    parser.add_argument('--qc_subdir', '-qs', type=str,
                        help='ExtraQC output directory name.')

    parser.add_argument('--standard_dir', '-std', type=str,
                        help='Root of a standard dataset to compare to.')

    parser.add_argument('--config', '-c', type=str,
                        default='/data/predict/data_from_nda/MRI_ROOT/'
                                'standard_templates.cfg',
                        help='configuration file for standard tempates.')

    parser.add_argument('--mriqc', '-mriqc', action='store_true',
                        help='Run MRIQC following conversion.')

    parser.add_argument('--fmriprep', '-fmriprep', action='store_true',
                        help='Run FMRIPREP following conversion.')

    parser.add_argument('--dwipreproc', '-dwipreproc', action='store_true',
                        help='Run DWI preprocessing following conversion.')

    parser.add_argument('--nifti_dir', '-nd', type=str, default=False,
                        help='Nifti root directory. If --nifti_dir is given, '
                             '--input will be ignored and dcm2niix will '
                             'not be ran.')

    parser.add_argument('--skip_dicom_rearrange', '-sdr',
                        action='store_true', default=False,
                        help='Skip dicom rearrange step.')

    parser.add_argument('--force_copy_dicom_to_source', '-fc', default=False,
                        action='store_true',
                        help='Force copy dicom files to sourcedata.')


    parser.add_argument('--skip_heudiconv', '-sh', default=False,
                        action='store_true',
                        help='Skip heudiconv step.')

    parser.add_argument('--force_heudiconv', '-fh', default=False,
                        action='store_true',
                        help='Force re-running heudiconv step.')

    parser.add_argument('--skip_qc', '-sq', default=False,
                        action='store_true',
                        help='Skip quick QC step.')

    parser.add_argument('--quick_scan', '-qqs', default=False,
                        action='store_true',
                        help='Assuming single series under a directory')

    parser.add_argument('--additional_recipients', '-ar',
                        nargs='+',
                        type=str, default=[],
                        help='List of recipients.')

    parser.add_argument('--run_all', '-ra', default=False,
                        action='store_true',
                        help='Run all sessions.')


    # extra options
    args = parser.parse_args(argv)

    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    config = configparser.ConfigParser()
    config.read(args.config)

    if args.run_all:
        root_dir = Path('/data/predict/data_from_nda')
        mri_root = root_dir / 'MRI_ROOT'
        mri_paths = root_dir.glob('*/PHOENIX/*/*/raw/*/mri/*')
        for i in [x for x in mri_paths if x.is_dir()]:
            if re.search('[A-Z]{2}\d{5}_MR_\d{4}_\d{2}_\d{2}_\d', i.name):
                subject_id = i.name.split('_')[0]
                date = i.name.split('_MR_')[1]

                # read standard template data
                site = i.name[:2]
                standard_dir = config.get('First Scan', site)

                # update args
                args.input = str(i)
                args.subject_name = subject_id
                args.session_name = date
                args.bids_root = mri_root
                args.standard_dir = standard_dir
                args.mriqc = True
                args.fmriprep = True
                args.dwipreproc = True
                args.skip_dicom_rearrange = True
                print(args)
                dicom_to_bids_QQC(args)
        sys.exit('Finished with run all option')

    logging.basicConfig(
        filename=args.bids_root + '/dicom_to_dpacc_bids.log',
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

    site = args.subject_name[:2]

    if args.standard_dir is None:
        try:
            args.standard_dir = config.get('First Scan', site)
        except:
            # TODO: update to default standard template?
            args.standard_dir = args.standard_dir


    dicom_to_bids_QQC(args)
    logger.info('Completed')

