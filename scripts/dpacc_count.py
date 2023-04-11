import argparse
from argparse import RawTextHelpFormatter
import sys
from pathlib import Path
import logging
from ampscz_asana.lib.mri_count import \
        count_and_make_it_available_for_dpdash, merge_zip_db_and_runsheet_db


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
        description='''Convert dicoms to BIDS

    mri_count.py \\
        --phoenix_roots /data/phoenix1 /data/phoenix2 \\
        --mriflow_csv /data/mri_flow.csv \\
        --dpdash_outpath /data/dpdash_out''',
        formatter_class=RawTextHelpFormatter)

    data_root = Path('/data/predict1/data_from_nda')
    phoenix_paths = [data_root / 'Pronet/PHOENIX',
                     data_root / 'Prescient/PHOENIX']
    mriflow_dir = data_root / 'MRI_ROOT/flow_check'
    mriflow_csv = mriflow_dir / 'mri_data_flow.csv'
    final_qc_dir = data_root / 'MRI_ROOT/derivatives/google_qc'
    dpdash_outpath = data_root / 'MRI_ROOT/eeg_mri_count'

    # image input related options
    parser.add_argument('--phoenix_roots', '-pr', nargs='+',
            default=phoenix_paths,
            help='Roots of PHOENIX directory')

    parser.add_argument('--mriflow_csv', '-mc', type=str,
            default=mriflow_csv,
            help='MRI dataflow (run sheet) summary csv')

    parser.add_argument('--final_qc_dir', '-fqc', type=str,
            default=final_qc_dir,
            help='Root of final QC measure csv files')

    parser.add_argument('--dpdash_outpath', '-o', type=str,
            default=dpdash_outpath,
            help='Directory to save DPDash loadable count csv files')

    parser.add_argument('--loglevel', '-l',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='WARNING',
            help='Log level to display (default: WARNING)')

    # extra options
    args = parser.parse_args(argv)
    args.phoenix_roots = [Path(x) for x in args.phoenix_roots]
    args.mriflow_csv = Path(args.mriflow_csv)
    args.dpdash_outpath = Path(args.dpdash_outpath)

    return args

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    logging.basicConfig(
            level=args.loglevel,
            format=' %(name)s :: %(levelname)-8s :: %(message)s',
            handlers=[logging.StreamHandler()])

    for modality in 'eeg', 'mri':
        count_and_make_it_available_for_dpdash(args.phoenix_roots,
                                               args.mriflow_csv,
                                               args.dpdash_outpath,
                                               args.final_qc_dir,
                                               modality=modality)


    # merge zip database with the run sheet database
    logging.info('Merging zip DB with run sheet DB')
    zip_df_loc = args.dpdash_outpath / 'mri_zip_db.csv'
    runsheet_df_loc = args.mriflow_csv
    output_merged_zip = args.dpdash_outpath / 'mri_all_db.csv'
    merge_zip_db_and_runsheet_db(zip_df_loc,
                                 runsheet_df_loc,
                                 output_merged_zip)
    logging.info(f'{output_merged_zip} is created')

    logging.info('completed')
