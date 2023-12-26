import sys
import pandas as pd
from pathlib import Path
import argparse
from argparse import RawTextHelpFormatter
from ampscz_asana.lib.qc import get_run_sheet_df, dataflow_dpdash
from qqc.utils.dpdash import get_summary_included_ids


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

    parser.add_argument('--skip_db_build', '-s', default=False,
                        action='store_true',
                        help='Skip re-building dataflow database')

    parser.add_argument('--test', '-t', default=False,
                        action='store_true', help='Test')

    args = parser.parse_args(argv)

    # extra options
    args.outdir = Path(args.outdir)
    args.phoenix_roots = [Path(x) for x in args.phoenix_roots]

    return args


if __name__ == '__main__':
    """The functions below are moved to dpacc_count.py"""
    args = parse_args(sys.argv[1:])


    csv_out = args.outdir / 'mri_data_flow.csv'

    if args.skip_db_build and csv_out.is_file():
        df = pd.read_csv(csv_out)

    else:
        df = pd.DataFrame()
        for phoenix_root in args.phoenix_roots:
            print(f'Summarizing dataflow in {phoenix_root}')
            df_tmp = get_run_sheet_df(phoenix_root,
                                      test=args.test)
            df = pd.concat([df, df_tmp])
        df['entry_date'] = df['entry_date'].dt.strftime('%Y-%m-%d')
        df.to_csv(csv_out)
                                                        

    if args.dpdash:
        print(f'Creating dpdash loadable csv files')
        df = pd.read_csv('/data/predict1/data_from_nda/MRI_ROOT/eeg_mri_count/mri_all_db.csv')

        # only include subjects in forms-qc summary
        forms_summary_ids = get_summary_included_ids()
        df = df[df.subject.isin(forms_summary_ids)]

        dataflow_dpdash(df, args.outdir)


