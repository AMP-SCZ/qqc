import re
import pandas as pd
from configparser import ConfigParser
from pathlib import Path
from typing import Dict
from ampscz_asana.models import drop_all_tables
from ampscz_asana.models.base import Base
from ampscz_asana.crawlers.subject import add_subjects, update_subjects
from ampscz_asana.crawlers.sessions import add_session_date
from ampscz_asana.crawlers.runsheets import add_run_sheets
from ampscz_asana.crawlers.qqc import add_qqc
from ampscz_asana.crawlers.mrizip import update_mri_zip
from ampscz_asana.crawlers.dwi import add_dwi, add_dwi_ap_pa, add_denoise, \
        add_freewater, add_skeletonization, add_eddy, add_cnn_masking, \
        add_topup, add_unring, run_denoise, run_skeletonization, \
        run_freewater
from ampscz_asana.utils import config
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from multiprocessing import Process



def remove_all_data(keys):
    engine = create_engine(
            f'postgresql://{keys["id"]}:{keys["password"]}'
            f'@{keys["host"]}:{keys["port"]}/{keys["db_name"]}')

    drop_all_tables(engine)
    Base.metadata.drop_all(engine)


def update_db(db_session):
    phoenix_roots = ['/data/predict1/data_from_nda/Pronet/PHOENIX',
                     '/data/predict1/data_from_nda/Prescient/PHOENIX']

    # # last modified for zip file?
    # add_subjects(db_session, phoenix_roots)
    # add_session_date(db_session)
    # add_run_sheets(db_session)

    # # why update multiple qqc sessions in every run?
    # add_qqc(db_session)

    # update_mri_zip(db_session)
    # update_subjects(db_session, phoenix_roots)

    # add dwi
    # add_dwi(db_session)
    # add_dwi_ap_pa(db_session)
    # add_unring(db_session)
    # add_denoise(db_session)
    # add_topup(db_session)
    add_eddy(db_session)
    add_cnn_masking(db_session)
    add_freewater(db_session)
    add_skeletonization(db_session)

    db_session.close()


def update_post_qqc_db(db_session):
    add_dwi(db_session)
    dwi = Dwi(qqc_id=qqc.id, pa_data=True, ap1_data=True, ap2_data=False)
    session.add(dwi)
    session.commit()

    anat = Anat(qqc_id=qqc.id, t1w_data=True, t2w_data=False)
    session.add(anat)
    session.commit()

    fmri = fMRI(qqc_id=qqc.id, ap1=True, pa1=True,
                ap2=True, pa2=True)
    session.add(fmri)
    session.commit()
    session.close()

    print("Data added to the PostgreSQL database using SQLAlchemy.")
    session = Session()


def get_db_session():
    # Create an engine and establish a session
    keys = config('/data/predict1/home/kcho/keys/.database_key',
                  'mri_analysis_db')
    # remove_all_data(keys)
    engine = create_engine(f'postgresql://{keys["id"]}:{keys["password"]}'
                           f'@{keys["host"]}:{keys["port"]}/{keys["db_name"]}')

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    return db_sesion

if __name__ == '__main__':
    # Create an engine and establish a session
    keys = config('/data/predict1/home/kcho/keys/.database_key',
                  'mri_analysis_db')
    # remove_all_data(keys)
    engine = create_engine(f'postgresql://{keys["id"]}:{keys["password"]}'
                           f'@{keys["host"]}:{keys["port"]}/{keys["db_name"]}')

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    update_db(db_session)

    
    # print("Running denoise")
    # run_denoise()
    run_skeletonization()
    # run_freewater()
    # print("Main process exiting")

    # update_post_qqc_db(keys)

    # test_query(session)
