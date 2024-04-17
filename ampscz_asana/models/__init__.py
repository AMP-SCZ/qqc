from ampscz_asana.models.subject import Subject
from ampscz_asana.models.mrizip import MriZip
from ampscz_asana.models.session import SessionDate, SessionNum
from ampscz_asana.models.runsheet import MriRunSheet, NoMri, MissingMri
from ampscz_asana.models.qqc import Qqc
from ampscz_asana.models.dwi import Dwi, DwiAP, DwiPA, DwiAPUnring, \
        DwiPAUnring, DwiAPDenoise, DwiPADenoise, DwiTopup, DwiEddy, \
        DwiCNNMasking, DwiFreewater, DwiSkeletonization
from ampscz_asana.models.anat import Anat, Mriqc, Freesurfer
from ampscz_asana.models.fmri import fMRI, fMRIPrep


def drop_all_tables(engine):
    tables_to_drop = [DwiSkeletonization, DwiFreewater, DwiCNNMasking,
                      DwiEddy, DwiTopup,
                      DwiAPUnring, DwiPAUnring,
                      DwiAPDenoise, DwiPADenoise,
                      DwiAP, DwiPA,
                      Mriqc, Freesurfer,
                      fMRIPrep,
                      Anat, fMRI, Dwi,
                      Qqc, MissingMri, NoMri, MriRunSheet,
                      SessionNum, SessionDate,
                      MriZip, Subject]

    # Drop tables in the specified order
    for table in tables_to_drop:
        table.__table__.drop(engine, checkfirst=True)
