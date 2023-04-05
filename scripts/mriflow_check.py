import argparse
from argparse import RawTextHelpFormatter
import sys
from pathlib import Path
from ampscz_asana.lib.qc import get_run_sheet_df, dataflow_dpdash
import pandas as pd


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
        description='''Convert dicoms to BIDS

    mriflow_check.py \\
        --outdir /data/predict1/data_from_nda/MRI_ROOT/flow_check \\
        --gspread_json /data/google_cred.json \\
        --test_run''',
        formatter_class=RawTextHelpFormatter)

    # image input related options
    default_out = '/data/predict1/data_from_nda/MRI_ROOT/flow_check'
    parser.add_argument('--outdir', '-o', type=str,
                        default=default_out,
                        help='Directory to save MRI dataflow outputs.')

    parser.add_argument('--phoenix_roots', '-p', nargs='+',
            default=['/data/predict1/data_from_nda/Pronet/PHOENIX',
                     '/data/predict1/data_from_nda/Prescient/PHOENIX'],
            help='List of PHOENIX paths to summarize MRI dataflow')

    parser.add_argument('--dpdash', '-d', default=False,
                        action='store_true',
                        help='Create DPDash importable CSVs')

    parser.add_argument('--test', '-t', default=False,
                        action='store_true', help='Test')

    args = parser.parse_args(argv)

    # extra options
    args.outdir = Path(args.outdir)
    args.phoenix_roots = [Path(x) for x in args.phoenix_roots]

    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    df = pd.DataFrame()
    for phoenix_root in args.phoenix_roots:
        df_tmp = get_run_sheet_df(phoenix_root)
        df = pd.concat([df, df_tmp])

    df.to_csv(args.outdir / 'mri_data_flow.csv')

    if args.dpdash:
        dataflow_dpdash(df)
