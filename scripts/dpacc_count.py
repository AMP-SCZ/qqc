import sys
import logging
import argparse
import pandas as pd
from pathlib import Path
from ampscz_asana.lib.mri_count import \
    count_and_make_it_available_for_dpdash, \
    merge_zip_db_and_runsheet_db
from ampscz_asana.lib.qc import get_run_sheet_df, dataflow_dpdash
from qqc.utils.dpdash import get_summary_included_ids


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
        description='''Convert dicoms to BIDS

    mri_count.py \\
        --phoenix_roots /data/phoenix1 /data/phoenix2 \\
        --mriflow_csv /data/mri_flow.csv \\
        --dpdash_outpath /data/dpdash_out''',
        formatter_class=argparse.RawTextHelpFormatter)

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

    # additional options
    parser.add_argument('--test', action='store_true',
            help='Test mode')

    # extra options
    args = parser.parse_args(argv)
    args.phoenix_roots = [Path(x) for x in args.phoenix_roots]
    args.mriflow_csv = Path(args.mriflow_csv)
    args.dpdash_outpath = Path(args.dpdash_outpath)

    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    # Configure logging
    logging.basicConfig(
            level=args.loglevel,
            format='%(asctime)s :: %(name)s :: %(levelname)-8s :: %(message)s',
            handlers=[
                    logging.StreamHandler(),  # Output to terminal
                    logging.FileHandler('logfile.log')  # Output to log file
            ])
    logger = logging.getLogger(__name__)
    logger.info('Starting the script')
    
    # Read all available run sheets from PHOENIX and create db (MRI)
    logger.info('Read information from AMP-SCZ REDCap and RPMS')
    df = pd.DataFrame()
    for phoenix_root in args.phoenix_roots:
        logger.info(f'Summarizing dataflow in {phoenix_root}')
        df_tmp = get_run_sheet_df(phoenix_root,
                                  test=args.test)
        df = pd.concat([df, df_tmp])
    df['entry_date'] = df['entry_date'].dt.strftime('%Y-%m-%d')
    df.to_csv(args.mriflow_csv)

    # Count data and make DPDasah readable CSV files
    for modality in 'eeg', 'mri':
        logger.info(f'Count and make counts available for DPDash: {modality}')
        count_and_make_it_available_for_dpdash(args.phoenix_roots,
                                               args.mriflow_csv,
                                               args.dpdash_outpath,
                                               args.final_qc_dir,
                                               modality=modality,
                                               sync_to_forms_id=False)
        logger.info(f'{modality}_zip_db.csv is created')

    # merge zip database with the run sheet database
    logger.info('Extra processing for MRI datatype')
    zip_df_loc = args.dpdash_outpath / 'mri_zip_db.csv'
    runsheet_df_loc = args.mriflow_csv
    output_merged_zip = args.dpdash_outpath / 'mri_all_db.csv'
    logger.info(f'Merging zip DB with run sheet DB to {output_merged_zip}')
    merge_zip_db_and_runsheet_db(zip_df_loc,
                                 runsheet_df_loc,
                                 output_merged_zip)
    logger.info(f'{output_merged_zip} is created')
    
    logger.info(f'Creating dpdash loadable csv files')
    df = pd.read_csv(output_merged_zip)
    # only include subjects in forms-qc summary
    forms_summary_ids = get_summary_included_ids()
    df = df[df.subject.isin(forms_summary_ids)]
    dataflow_dpdash(df, args.mriflow_csv.parent)
    logger.info('completed')

    # MRIQC value match to dataflow DF
    logger.info('Update MRIQC dpdash table according to dataflow table')
    count_and_make_it_available_for_dpdash(args.phoenix_roots,
                                           args.mriflow_csv,
                                           args.dpdash_outpath,
                                           args.final_qc_dir,
                                           modality='mri',
                                           sync_to_forms_id=True)
