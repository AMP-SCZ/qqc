import sys
import argparse
from argparse import RawTextHelpFormatter
from pathlib import Path
from AMPSCZ_pipeline.lib.server_scanner import grep_subject_files, \
        send_to_caselist
import asana
from AMPSCZ_pipeline.lib.asana_api import get_asana_ready, create_new_task



def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
        description='''ASANA pipeline for AMPSCZ

    asana_pipeline.py \\
        --phoenix_paths \\
            ${raw_dicom_dir}/human_pilot/data/dicom \\
            ${raw_dicom_dir}/human_pilot/data/dicom \\
            ${raw_dicom_dir}/human_pilot/data/dicom \\
            ${raw_dicom_dir}/human_pilot/data/dicom''',
        formatter_class=RawTextHelpFormatter)

    # image input related options
    parser.add_argument('--phoenix_paths', '-pp', nargs='+',
                        help='List of PHOENIX PATHS')

    args = parser.parse_args(argv)
    return args


def run_asana_pipeline():
    phoenix_dirs = [
        Path('/data/predict/data_from_nda/Pronet/PHOENIX'),
        Path('/data/predict/data_from_nda/Prescient/PHOENIX')
    ]
    db_loc = '/data/predict/kcho/software/asana_pipeline/kcho/asana_db.txt'

    client, workspace_gid, project_gid = get_asana_ready()
    for phoenix_dir in phoenix_dirs:
        print('Beginning of the Simone pipeline')
        subject_files_list = grep_subject_files(phoenix_dir)

        for subject_id in subject_files_list:
            potential_subject = send_to_caselist(subject_id, db_loc)

            if potential_subject is not None:
                print('we are creating a task')
                create_new_task(client, potential_subject,
                                workspace_gid, project_gid)

    print("Completed")


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    run_asana_pipeline()


