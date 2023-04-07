import argparse
from argparse import RawTextHelpFormatter
import sys
from pathlib import Path
import logging
from ampscz_asana.lib.mri_count import \
        count_and_make_it_available_for_dpdash


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
        description='''Convert dicoms to BIDS

,   mri_count.py \\
        --phoenix_roots /data/phoenix1 /data/phoenix2 \\
        --mriflow_csv /data/mri_flow.csv \\
        --dpdash_outpath /data/dpdash_out''',
        formatter_class=RawTextHelpFormatter)

    data_root = Path('/data/predict1/data_from_nda')
    phoenix_paths = [data_root / 'Pronet/PHOENIX',
                     data_root / 'Prescient/PHOENIX']
    mriflow_dir = data_root / 'MRI_ROOT/flow_check'
    mriflow_csv = mriflow_dir / 'mri_data_flow.csv'
    dpdash_outpath = data_root / 'MRI_ROOT/eeg_mri_count'

    # image input related options
    parser.add_argument('--phoenix_roots', '-pr', nargs='+',
            default=phoenix_paths,
            help='Roots of PHOENIX directory')

    parser.add_argument('--mriflow_csv', '-mc', type=str,
            default=mriflow_csv,
            help='MRI dataflow summary csv')

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
                                               modality=modality)

    logging.info('completed')
