from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ampscz_asana.models.base import Base
from multiprocessing import Process, Queue
import subprocess
from pathlib import Path


class Dwi(Base):
    __tablename__ = 'dwi'

    id = Column(Integer, primary_key=True)
    qqc_id = Column(Integer, ForeignKey('qqc.id'))
    full_data = Column(Boolean)
    extra_data = Column(Boolean)
    output_loc = Column(String(255))

    dwi_aps = relationship("DwiAP", backref="dwi")
    dwi_pas = relationship("DwiPA", backref="dwi")
    topup = relationship("DwiTopup", backref="dwi")

    def __str__(self):
        return f"Dwi({self.output_loc})"

    def __repr__(self):
        return self.__str__()


class DwiAP(Base):
    __tablename__ = 'dwi_ap'

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    dwi_id = Column(Integer, ForeignKey('dwi.id'))
    filename = Column(String(255))
    to_be_used = Column(Boolean)

    unring = relationship("DwiAPUnring", backref="data")
    denoise = relationship("DwiAPDenoise", backref="data")

    def __str__(self):
        return f"DwiAP({self.filename})"

    def __repr__(self):
        return self.__str__()


class DwiPA(Base):
    __tablename__ = 'dwi_pa'

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    dwi_id = Column(Integer, ForeignKey('dwi.id'))
    filename = Column(String(255))
    to_be_used = Column(Boolean)

    unring = relationship("DwiPAUnring", backref="data")
    denoise = relationship("DwiPADenoise", backref="data")

    def __str__(self):
        return f"DwiPA({self.filename})"

    def __repr__(self):
        return self.__str__()


class DwiAPUnring(Base):
    __tablename__ = 'dwi_ap_unring'

    id = Column(Integer, primary_key=True)
    dwi_ap_id = Column(Integer, ForeignKey('dwi_ap.id'))
    filename = Column(String(255))
    running = Column(Boolean)
    processed = Column(Boolean)

    topup = relationship("DwiTopup", backref="dwi_ap_unring")

    def __str__(self):
        return f"DwiAPUnring({self.filename})"

    def __repr__(self):
        return self.__str__()


class DwiPAUnring(Base):
    __tablename__ = 'dwi_pa_unring'

    id = Column(Integer, primary_key=True)
    dwi_pa_id = Column(Integer, ForeignKey('dwi_pa.id'))
    filename = Column(String(255))
    running = Column(Boolean)
    processed = Column(Boolean)

    topup = relationship("DwiTopup", backref="dwi_pa_unring")

    def __str__(self):
        return f"DwiPAUnring({self.filename})"

    def __repr__(self):
        return self.__str__()


class DwiAPDenoise(Base):
    __tablename__ = 'dwi_ap_denoise'

    id = Column(Integer, primary_key=True)
    dwi_ap_id = Column(Integer, ForeignKey('dwi_ap.id'))
    filename = Column(String(255))
    running = Column(Boolean)
    processed = Column(Boolean)

    topup = relationship("DwiTopup", backref="dwi_ap_denoise")

    def get_command(self):
        output_loc = Path(self.data.dwi.output_loc)
        rawdata_dir = Path(self.data.dwi.qqc.rawdata_dir)
        input_file = rawdata_dir / 'dwi' / self.data.filename
        output_file = output_loc / self.filename
        command = '/data/pnl/kcho/miniforge3/envs/mrtrix/bin/dwidenoise ' \
                f'{input_file} {output_file}'
        return command

    def __str__(self):
        return f"DwiAPDenoise({self.filename})"

    def __repr__(self):
        return self.__str__()


class DwiPADenoise(Base):
    __tablename__ = 'dwi_pa_denoise'

    id = Column(Integer, primary_key=True)
    dwi_pa_id = Column(Integer, ForeignKey('dwi_pa.id'))
    filename = Column(String(255))
    running = Column(Boolean)
    processed = Column(Boolean)

    topup = relationship("DwiTopup", backref="dwi_pa_denoise")

    def get_command(self):
        output_loc = Path(self.data.dwi.output_loc)
        rawdata_dir = Path(self.data.dwi.qqc.rawdata_dir)
        input_file = rawdata_dir / 'dwi' / self.data.filename
        output_file = output_loc / self.filename
        command = '/data/pnl/kcho/miniforge3/envs/mrtrix/bin/dwidenoise ' \
                f'{input_file} {output_file}'
        return command

    def __str__(self):
        return f"DwiPADenoise({self.filename})"

    def __repr__(self):
        return self.__str__()


class DwiTopup(Base):
    __tablename__ = 'dwi_topup'

    id = Column(Integer, primary_key=True)
    dwi_id = Column(Integer, ForeignKey('dwi.id'))
    dwi_ap_unring_id = Column(Integer, ForeignKey('dwi_ap_unring.id'))
    dwi_pa_unring_id = Column(Integer, ForeignKey('dwi_pa_unring.id'))
    dwi_ap_denoise_id = Column(Integer, ForeignKey('dwi_ap_denoise.id'))
    dwi_pa_denoise_id = Column(Integer, ForeignKey('dwi_pa_denoise.id'))
    filename = Column(String(255))
    running = Column(Boolean)
    processed = Column(Boolean)

    eddy = relationship("DwiEddy", backref="topup", uselist=False)

    def __str__(self):
        return f"DwiTopup({self.filename})"

    def __repr__(self):
        return self.__str__()


class DwiEddy(Base):
    __tablename__ = 'dwi_eddy'

    id = Column(Integer, primary_key=True)
    topup_id = Column(Integer, ForeignKey('dwi_topup.id'))
    processed = Column(Boolean)
    running = Column(Boolean)

    cnn_masking = relationship("DwiCNNMasking",
                               backref="dwi_eddy",
                               uselist=False)

    freewater = relationship("DwiFreewater",
                               backref="dwi_eddy",
                               uselist=False)


class DwiCNNMasking(Base):
    __tablename__ = 'dwi_cnnmasking'

    id = Column(Integer, primary_key=True)
    eddy_id = Column(Integer, ForeignKey('dwi_eddy.id'))
    processed = Column(Boolean)
    running = Column(Boolean)

    freewater = relationship("DwiFreewater",
                             backref="cnn_masking",
                             uselist=False)


class DwiFreewater(Base):
    __tablename__ = 'dwi_freewater'

    id = Column(Integer, primary_key=True)
    cnnmasking_id = Column(Integer, ForeignKey('dwi_cnnmasking.id'))
    eddy_id = Column(Integer, ForeignKey('dwi_eddy.id'))
    running = Column(Boolean)
    processed = Column(Boolean)

    skeleton = relationship("DwiSkeletonization",
                             backref="freewater",
                             uselist=False)

    def run_freewater(self):
        import sys
        sys.path.append('/data/predict1/home/kcho/software/objPipe_for_freewater_u24')
        from objPipe.freewater.freewater import FreewaterPipe
        from objPipe.utils.run import RunCommand

        class fsPipe(FreewaterPipe, RunCommand):
            pass
            # def __init__(self):
                # RunCommand.__init__(self)

        freewaterPipe = fsPipe(RunCommand)
        freewaterPipe.matlab = '/apps/lib-osver/matlab/2021b/bin/matlab'
        freewaterPipe.fw_script_dir = '/data/predict1/home/kcho/software/Free-Water'

        dwi = self.dwi_eddy.topup.dwi
        output_loc = Path(dwi.output_loc)
        qqc = self.dwi_eddy.topup.dwi.qqc
        session_num = qqc.session_num
        session_date = session_num.session_date
        mri_zip = session_date.mri_zip
        subject = mri_zip.subject

        fw_dir = output_loc / 'fw'
        freewaterPipe.fw = fw_dir / f"{subject.subject_id}_FW.nii.gz"
        freewaterPipe.fw_dir = fw_dir
        freewaterPipe.subject_name = f'sub-{subject.subject_id}'
        freewaterPipe.diff_eddy_out = output_loc / \
                f'sub-{subject.subject_id}_eddy_out.nii.gz'
        freewaterPipe.diff_raw_bval = output_loc / \
                f'sub-{subject.subject_id}_raw_bval_merged.bval'
        freewaterPipe.diff_eddy_out_bvec = output_loc / \
                f'sub-{subject.subject_id}_eddy_out.eddy_rotated_bvecs'
        freewaterPipe.diff_mask = output_loc / \
                f'mask_cnn.nii.gz'
        freewaterPipe.bsub = False
        freewaterPipe.force = False
        freewaterPipe.run_freewater()


class DwiSkeletonization(Base):
    __tablename__ = 'dwi_skel'

    id = Column(Integer, primary_key=True)
    freewater_id = Column(Integer, ForeignKey('dwi_freewater.id'))
    processed = Column(Boolean)
    running = Column(Boolean)

    def get_command(self):
        output_loc = Path(self.freewater.dwi_eddy.topup.dwi.output_loc)
        tbss_dir = output_loc / 'tbss'
        tbss_dir.mkdir(exist_ok=True)
        sub = tbss_dir.parent.parent.name
        ses = tbss_dir.parent.name
        sub_ses = f"{sub}_{ses}"
        
        caselist_loc = tbss_dir / 'caselist.csv'
        with open(caselist_loc, 'w') as fp:
            fp.write(sub_ses)

        imagelist_loc = tbss_dir / 'imagelist.csv'
        fw_dir = output_loc / 'fw'
        fa_file = fw_dir / f"{sub}_FA.nii.gz"
        fat_file = fw_dir / f"{sub}_fwcor_FA.nii.gz"
        md_file = fw_dir / f"{sub}_MD.nii.gz"
        fw_file = fw_dir / f"{sub}_FW.nii.gz"
        with open(imagelist_loc, 'w') as fp:
            fp.write(f"{fa_file},{fat_file},{fw_file},{md_file}")

        command = 'ANTSPATH=/data/pnl/kcho/miniforge3/bin '
        command += '/data/predict1/home/kcho/software/TBSS/lib/tbss_all ' \
            f'-i {imagelist_loc} ' \
            f'-c {caselist_loc} ' \
            f'--modality FA,FAt,FW,MD ' \
            '--enigma ' \
            f'-o {tbss_dir / "tbss_out"}'

        return command

    def __str__(self):
        return f"DwiSkeletonization({self.id})"

    def __repr__(self):
        return self.__str__()
