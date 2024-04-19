import re
import pandas as pd
from pathlib import Path
from datetime import datetime
from ampscz_asana.models.dwi import Dwi, DwiAP, DwiPA, \
        DwiAPUnring, DwiPAUnring, DwiAPDenoise, DwiPADenoise, \
        DwiTopup, DwiEddy, DwiCNNMasking, DwiFreewater, DwiSkeletonization
from ampscz_asana.crawlers.mrizip import match_mriZip
from ampscz_asana.crawlers.qqc import Qqc
from subprocess import Popen, PIPE, run
import multiprocessing
# from ampscz_asana.crawlers.update_db import get_db_session


def run_command(command):
    print(f'Running {command}')
    run(command, stdout=PIPE, stderr=PIPE, shell=True)


def add_dwi(db_session):
    dwi_root = Path('/data/predict1/data_from_nda/MRI_ROOT/'
                    'derivatives/dwipreproc_fsl_6078')
    qqc_objs = db_session.query(Qqc).filter_by(qqc_completed=True).all()

    for qqc_obj in qqc_objs:
        dwi_obj = db_session.query(Dwi).filter_by(qqc_id=qqc_obj.id).first()
        if dwi_obj is None:
            sessionNum = qqc_obj.session_num
            sessionDate = sessionNum.session_date
            session_str = sessionDate.session_date.strftime('%Y%m%d')

            subject_id = sessionDate.mri_zip.subject.subject_id
            sub_ses = f'sub-{subject_id}/' \
                      f'ses-{session_str}{sessionNum.session_num}'
            output_loc = dwi_root / sub_ses
            dwi_raw_dir = Path(qqc_obj.rawdata_dir) / 'dwi'
            if dwi_raw_dir.is_dir():
                dwi_obj = Dwi(qqc_id=qqc_obj.id,
                              output_loc=str(output_loc))
                print(f'Adding Dwi object: {dwi_obj}')
                db_session.add(dwi_obj)
                db_session.commit()
        else:
            print(f'Skipping adding Dwi object for {qqc_obj}')


def add_dwi_ap_pa(db_session):
    dwis = db_session.query(Dwi).all()
    for dwi in dwis:
        qqc_obj = dwi.qqc
        dwi_raw_dir = Path(qqc_obj.rawdata_dir) / 'dwi'
        AP_nifti_locs = dwi_raw_dir.glob('*dir-AP*dwi.nii.gz')
        for AP_nifti_loc in AP_nifti_locs:
            try:
                run_num = re.search('dir-AP_run-(\d)_dwi.nii.gz',
                                    AP_nifti_loc.name).group(1)
            except AttributeError:
                continue

            dwiApObj = db_session.query(DwiAP).filter_by(
                    filename=AP_nifti_loc.name).first()
            if dwiApObj is None:
                dwiAp = DwiAP(number=run_num, dwi_id=dwi.id,
                              filename=AP_nifti_loc.name)
                print(f'Adding DwiAP object: {dwiAp}')
                db_session.add(dwiAp)
                db_session.commit()
            else:
                print(f'Not adding {AP_nifti_loc.name}')

        PA_nifti_locs = dwi_raw_dir.glob('*dir-PA*dwi.nii.gz')
        for PA_nifti_loc in PA_nifti_locs:
            try:
                run_num = re.search('dir-PA_run-(\d)_dwi.nii.gz',
                                    PA_nifti_loc.name).group(1)
            except AttributeError:
                continue

            dwiPaObj = db_session.query(DwiPA).filter_by(
                    filename=PA_nifti_loc.name).first()
            if dwiPaObj is None:
                dwiPa = DwiPA(number=run_num, dwi_id=dwi.id,
                              filename=PA_nifti_loc.name)
                print(f'Adding DwiPA object: {dwiPa}')
                db_session.add(dwiPa)
                db_session.commit()
            else:
                print(f'Not adding {PA_nifti_loc.name}')


    # check if they are ordered well
    dwis = db_session.query(Dwi).filter(
            (Dwi.full_data.is_(None)) | (Dwi.full_data.is_(False))).all()
    # dwis = db_session.query(Dwi).all()
    for dwi in dwis:
        dwi_pas = dwi.dwi_pas
        pa_correct_num = False
        ap_correct_num = False

        if len(dwi_pas) == 1:
            dwi_pas[0].to_be_used = True
            db_session.commit()
            pa_correct_num = True
        dwi_aps = dwi.dwi_aps
        if len(dwi_aps) == 2:
            for dwi_ap in dwi_aps:
                dwi_ap.to_be_used = True
            ap_correct_num = True

        if ap_correct_num and pa_correct_num:
            dwi.full_data = True

        if len(dwi_pas) > 1 or len(dwi_aps) > 2:
            dwi.extra_data = True

        db_session.commit()


def add_unring(db_session):
    # unring
    # check if they are ordered well
    dwis = db_session.query(Dwi).filter_by(full_data=True).all()
    # dwis = db_session.query(Dwi).all()
    for dwi in dwis:
        qqc_obj = dwi.qqc
        sessionNum = qqc_obj.session_num
        sessionDate = sessionNum.session_date
        session_str = sessionDate.session_date.strftime('%Y%m%d')
        subject_id = sessionDate.mri_zip.subject.subject_id
        dwi_pas = dwi.dwi_pas
        dwi_aps = dwi.dwi_aps

        for dwi_pa in dwi_pas:
            dwi_pa_unring = db_session.query(DwiPAUnring).filter_by(
                    dwi_pa_id=dwi_pa.id).first()
            outfile = f'sub-{subject_id}_dwi_unring.nii.gz'
            if (Path(dwi.output_loc) / outfile).is_file():
                processed = True
            else:
                processed = False

            if dwi_pa_unring is None:
                dwi_pa_unring = DwiPAUnring(
                        dwi_pa_id = dwi_pa.id,
                        filename = outfile,
                        processed=processed)
                print(f'Adding DwiPAUnring object: {dwi_pa_unring}')
                db_session.add(dwi_pa_unring)
                db_session.commit()

            else:
                if dwi_pa_unring.processed == processed:
                    continue
                else:
                    print(f'Unring processed: {dwi_pa_unring}')
                    dwi_pa_unring.processed = processed
                    db_session.commit()

        for dwi_ap in dwi_aps:
            dwi_ap_unring = db_session.query(DwiAPUnring).filter_by(
                    dwi_ap_id=dwi_ap.id).first()
            outfile = f'sub-{subject_id}_dwi_blip_unring{dwi_ap.number}.nii.gz'
            if (Path(dwi.output_loc) / outfile).is_file():
                processed = True
            else:
                processed = False

            if dwi_ap_unring is None:
                dwi_ap_unring = DwiAPUnring(
                        dwi_ap_id = dwi_ap.id,
                        filename = outfile,
                        processed=processed)
                print(f'Adding DwiAPUnring object: {dwi_ap_unring}')
                db_session.add(dwi_ap_unring)
                db_session.commit()

            else:
                if dwi_ap_unring.processed == processed:
                    continue
                else:
                    print(f'Unring processed: {dwi_ap_unring}')
                    dwi_ap_unring.processed = processed
                    db_session.commit()


def add_denoise(db_session, process: bool = True):
    # unring
    # check if they are ordered well
    dwis = db_session.query(Dwi).filter_by(full_data=True).all()
    for dwi in dwis:
        qqc_obj = dwi.qqc
        sessionNum = qqc_obj.session_num
        sessionDate = sessionNum.session_date
        subject_id = sessionDate.mri_zip.subject.subject_id
        dwi_pas = dwi.dwi_pas
        dwi_aps = dwi.dwi_aps

        for dwi_pa in dwi_pas:
            dwi_pa_denoise = db_session.query(DwiPADenoise).filter_by(
                    dwi_pa_id=dwi_pa.id).first()
            outfile = f'sub-{subject_id}_dwi_denoise.nii.gz'
            if (Path(dwi.output_loc) / outfile).is_file():
                processed = True
            else:
                processed = False

            if dwi_pa_denoise is None:
                dwi_pa_denoise = DwiPADenoise(
                        dwi_pa_id = dwi_pa.id,
                        filename = outfile,
                        processed=processed)
                print(f'Adding DwiPADenoise object: {dwi_pa_denoise}')
                db_session.add(dwi_pa_denoise)
                db_session.commit()

            else:
                if dwi_pa_denoise.processed == processed:
                    continue
                else:
                    print(f'Denoising processed: {dwi_pa_denoise}')
                    dwi_pa_denoise.processed = processed
                    db_session.commit()

        for dwi_ap in dwi_aps:
            dwi_ap_denoise = db_session.query(DwiAPDenoise).filter_by(
                    dwi_ap_id=dwi_ap.id).first()
            outfile = f'sub-{subject_id}_dwi_blip_denoise{dwi_ap.number}.nii.gz'
            if (Path(dwi.output_loc) / outfile).is_file():
                processed = True
            else:
                processed = False

            if dwi_ap_denoise is None:
                dwi_ap_denoise = DwiAPDenoise(
                        dwi_ap_id = dwi_ap.id,
                        filename = outfile,
                        processed=processed)
                print(f'Adding DwiAPDenoise object: {dwi_ap_denoise}')
                db_session.add(dwi_ap_denoise)
                db_session.commit()

            else:
                if dwi_ap_denoise.processed == processed:
                    continue
                else:
                    print(f'Denoise processed: {dwi_ap_denoise}')
                    dwi_ap_denoise.processed = processed
                    db_session.commit()


def add_topup(db_session):
    # top up
    # check if they are ordered well
    dwis = db_session.query(Dwi).filter_by(full_data=True).all()
    # dwis = db_session.query(Dwi).all()
    for dwi in dwis:
        qqc_obj = dwi.qqc
        sessionNum = qqc_obj.session_num
        sessionDate = sessionNum.session_date
        session_str = sessionDate.session_date.strftime('%Y%m%d')
        subject_id = sessionDate.mri_zip.subject.subject_id
        topup = db_session.query(DwiTopup).filter_by(
                dwi_id=dwi.id).first()

        filename = 'hifi_b0.nii.gz'
        if (Path(dwi.output_loc) / filename).is_file():
            processed = True
        else:
            processed = False

        if topup is None:
            topup = DwiTopup(
                    dwi_id = dwi.id,
                    filename = filename,
                    processed = processed)
            db_session.add(topup)
            db_session.commit()
        else:
            if topup.processed == processed:
                continue
            else:
                topup.processed = processed
                db_session.commit()


def add_eddy(db_session):
    # eddy
    # check if they are ordered well
    topups = db_session.query(DwiTopup).all()
    # dwis = db_session.query(Dwi).all()
    for topup in topups:
        dwi = topup.dwi
        qqc_obj = dwi.qqc
        sessionNum = qqc_obj.session_num
        sessionDate = sessionNum.session_date
        session_str = sessionDate.session_date.strftime('%Y%m%d')
        subject_id = sessionDate.mri_zip.subject.subject_id

        eddy = db_session.query(DwiEddy).filter_by(
                topup_id=topup.id).first()

        filename = f'sub-{subject_id}_eddy_out.nii.gz'
        if (Path(dwi.output_loc) / filename).is_file():
            print('Eddy done')
            processed = True
        else:
            processed = False

        if eddy is None:
            eddy = DwiEddy(
                    topup_id = topup.id,
                    processed = processed)
            db_session.add(eddy)
            db_session.commit()
        else:
            if eddy.processed == processed:
                continue
            else:
                eddy.processed = processed
                db_session.commit()


def add_cnn_masking(db_session):
    # cnn masking
    # check if they are ordered well
    eddys = db_session.query(DwiEddy).all()
    # dwis = db_session.query(Dwi).all()
    for eddy in eddys:
        topup = eddy.topup
        dwi = topup.dwi
        qqc_obj = dwi.qqc
        sessionNum = qqc_obj.session_num
        sessionDate = sessionNum.session_date
        session_str = sessionDate.session_date.strftime('%Y%m%d')
        subject_id = sessionDate.mri_zip.subject.subject_id

        cnn_masking = db_session.query(DwiCNNMasking).filter_by(
                eddy_id=eddy.id).first()

        filename = 'mask_cnn.nii.gz'
        if (Path(dwi.output_loc) / filename).is_file():
            print('Masking done')
            processed = True
        else:
            processed = False

        if cnn_masking is None:
            cnn_masking = DwiCNNMasking(
                    eddy_id = eddy.id,
                    processed = processed)
            db_session.add(cnn_masking)
            db_session.commit()
        else:
            if cnn_masking.processed == processed:
                continue
            else:
                cnn_masking.processed = processed
                db_session.commit()


def add_freewater(db_session):
    eddys = db_session.query(DwiEddy).all()
    # dwis = db_session.query(Dwi).all()
    for eddy in eddys:
        topup = eddy.topup
        dwi = topup.dwi
        qqc_obj = dwi.qqc
        sessionNum = qqc_obj.session_num
        sessionDate = sessionNum.session_date
        session_str = sessionDate.session_date.strftime('%Y%m%d')
        subject_id = sessionDate.mri_zip.subject.subject_id
        cnn_masking = eddy.cnn_masking

        freewater = db_session.query(DwiFreewater).filter_by(
                eddy_id=eddy.id).first()

        filename = f'sub-{subject_id}_FW.nii.gz'
        outfile = Path(dwi.output_loc) / 'fw'/ filename
        if (Path(dwi.output_loc) / 'fw'/ filename).is_file():
            processed = True
        else:
            processed = False

        if freewater is None:
            freewater = DwiFreewater(
                    eddy_id = eddy.id,
                    cnnmasking_id = cnn_masking.id,
                    processed = processed)
            print(f'Adding Freewater object: {freewater}')
            db_session.add(freewater)
            db_session.commit()
        else:
            if freewater.processed == processed:
                continue
            else:
                freewater.processed = processed
                db_session.commit()


def add_skeletonization(db_session):
    freewaters = db_session.query(DwiFreewater).all()
    for freewater in freewaters:
        skel = db_session.query(DwiSkeletonization).filter_by(
                freewater_id=freewater.id).first()

        tbss_dir = Path(
            freewater.dwi_eddy.topup.dwi.output_loc
            ) / 'tbss' / 'tbss_out'
        stat_file = tbss_dir / 'stats' / 'MD_combined_roi_avg.csv'
        if stat_file.is_file():
            processed = True
        else:
            processed = False

        if skel is None:
            skel = DwiSkeletonization(
                    freewater_id = freewater.id,
                    processed = processed)
            print(f'Adding DwiSkeletonization object: {freewater}')
            db_session.add(skel)
            db_session.commit()
        else:
            if skel.processed == processed:
                continue
            else:
                skel.processed = processed
                db_session.commit()


def get_db_session():
    # Create an engine and establish a session
    from ampscz_asana.utils import config
    from sqlalchemy import create_engine
    from ampscz_asana.models.base import Base
    from sqlalchemy.orm import sessionmaker

    keys = config('/data/predict1/home/kcho/keys/.database_key',
                  'mri_analysis_db')
    # remove_all_data(keys)
    engine = create_engine(f'postgresql://{keys["id"]}:{keys["password"]}'
                           f'@{keys["host"]}:{keys["port"]}/{keys["db_name"]}')

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    return db_session

# def run_denoise(db_session):
def run_denoise():
    db_session = get_db_session()

    pool = multiprocessing.Pool(2)

    result_list = []
    def log_result(result):
        result_list.append(result)

    dwi_ap_denoises = db_session.query(DwiAPDenoise).all()
    for dwi_ap_denoise in dwi_ap_denoises:
        if not dwi_ap_denoise.processed:
            command = dwi_ap_denoise.get_command()

            # res = pool.apply_async(run_command, (command,))
            # p = Process(target=run_command, args=(queue, command))
            # p.start()
            # # p.join()
            # # result = queue.get()
            # print('Running in the background')
            try:
                res = pool.apply_async(run_command,
                        (command,),
                        callback=log_result)
            except Exception as e:
                logger.warning(e)
                with open(self.root_dir / 'error_caselist.txt', 'a') as fp:
                    fp.write(str(subses_classs.session) + f': {e}\n' )
        else:
            print('skip denoising: ', dwi_ap_denoise)

    dwi_pa_denoises = db_session.query(DwiPADenoise).all()
    for dwi_pa_denoise in dwi_pa_denoises:
        if not dwi_pa_denoise.processed:
            command = dwi_pa_denoise.get_command()

            try:
                res = pool.apply_async(run_command,
                        (command,),
                        callback=log_result)
            except Exception as e:
                logger.warning(e)
                with open(self.root_dir / 'error_caselist.txt', 'a') as fp:
                    fp.write(str(subses_classs.session) + f': {e}\n' )
        else:
            print('skip denoising: ', dwi_pa_denoise)

    pool.close()
    pool.join()


def run_skeletonization():
    db_session = get_db_session()

    pool = multiprocessing.Pool(10)

    result_list = []
    def log_result(result):
        result_list.append(result)

    freewaters = db_session.query(DwiFreewater).all()
    for freewater in freewaters:
        if freewater.processed:
            skeleton = freewater.skeleton
            if not skeleton.processed:
                command = skeleton.get_command()
                try:
                    res = pool.apply_async(run_command,
                            (command,),
                            callback=log_result)
                    continue
                except Exception as e:
                    logger.warning(e)
                    with open(self.root_dir / 'error_caselist.txt', 'a') as fp:
                        fp.write(str(subses_classs.session) + f': {e}\n' )

            # print('skip skeletonization: ', skel)
        else:
            print('freewater not processed: ', freewater)



    pool.close()
    pool.join()


    for freewater in freewaters:
        if freewater.processed:
            skeleton = freewater.skeleton
            if not skeleton.processed:
                tbss_dir = Path(
                    freewater.dwi_eddy.topup.dwi.output_loc
                    ) / 'tbss' / 'tbss_out'
                stat_file = tbss_dir / 'stats' / 'MD_combined_roi_avg.csv'
                if stat_file.is_file():
                    skeleton.processed = True
                    db_session.commit()



def run_freewater():
    db_session = get_db_session()

    pool = multiprocessing.Pool(4)

    result_list = []
    def log_result(result):
        result_list.append(result)

    freewaters = db_session.query(DwiFreewater).filter_by(processed=False)
    for freewater in freewaters:
        print('Going through:', freewater)
        eddy = freewater.dwi_eddy
        print(eddy.topup.dwi.qqc)
        cnn_masking = freewater.cnn_masking

        if eddy.processed and cnn_masking.processed:
            print('running freewater: ', freewater)
            freewater.run_freewater()
            filename = f'sub-{subject_id}_FW.nii.gz'
            outfile = Path(dwi.output_loc) / 'fw'/ filename
            if (Path(dwi.output_loc) / 'fw'/ filename).is_file():
                freewater.processed = True
                db_session.commit()
            break

    pool.close()
    pool.join()
