import os
import configparser
from pathlib import Path
import shutil


def copy_bval_bevc_for_GE(diff_dir, config_loc):
    config = configparser.ConfigParser()
    config.read(config_loc)

    ge_pa_bval = Path(config.get('GE diffusion', 'PA bval'))
    ge_pa_bvec = Path(config.get('GE diffusion', 'PA bvec'))
    ge_ap_bval = Path(config.get('GE diffusion', 'AP bval'))
    ge_ap_bvec = Path(config.get('GE diffusion', 'AP bvec'))

    # orig PA bval
    pa_bval_p = Path(diff_dir).glob('*-PA_*dwi.bval')
    pa_bvec_p = Path(diff_dir).glob('*-PA_*dwi.bvec')

    # orig AP bval
    ap_bval_p = Path(diff_dir).glob('*b0_*-AP_*dwi.bval')
    ap_bvec_p = Path(diff_dir).glob('*b0_*-AP_*dwi.bvec')

    # back up to orig
    for pathgen, ge_path in zip([pa_bval_p, pa_bvec_p,
                                 ap_bval_p, ap_bvec_p],
                                [ge_pa_bval, ge_pa_bvec,
                                 ge_ap_bval, ge_ap_bvec]):
        for path in pathgen:
            new_name = path.parent / f'{path.name}.bak'
            # backup
            shutil.copy(path, new_name)

            # overwrite the original bvec and bval
            shutil.copy(ge_path, path)


def test_copy_bval_bvec_for_GE():
    test_config = 'test_config.cfg'

    for i in 'test_pa', 'test_ap':
        for j in 'bval', 'bvec':
            with open(f'{i}.{j}', 'w') as fp:
                fp.write('new')

    with open(test_config, 'w') as fp:
        fp.write('[GE diffusion]\n')
        fp.write('PA bval = test_pa.bval\n')
        fp.write('PA bvec = test_pa.bvec\n')
        fp.write('AP bval = test_ap.bval\n')
        fp.write('AP bvec = test_ap.bvec\n')

    diff_dir = Path('test_diff')
    diff_dir.mkdir(exist_ok=True)

    (diff_dir / 'sub-xx_ses-202201011_acq-123_dir-PA_run-1_dwi.bval').touch()
    (diff_dir / 'sub-xx_ses-202201011_acq-123_dir-PA_run-1_dwi.bvec').touch()
    (diff_dir / 'sub-xx_ses-202201011_acq-b0_dir-AP_run-1_dwi.bval').touch()
    (diff_dir / 'sub-xx_ses-202201011_acq-b0_dir-AP_run-1_dwi.bvec').touch()
    (diff_dir / 'sub-xx_ses-202201011_acq-b0_dir-AP_run-2_dwi.bval').touch()
    (diff_dir / 'sub-xx_ses-202201011_acq-b0_dir-AP_run-2_dwi.bvec').touch()

    copy_bval_bevc_for_GE(diff_dir, 'test_config.cfg')

    with open(
            diff_dir / 'sub-xx_ses-202201011_acq-b0_dir-AP_run-2_dwi.bvec',
            'r') as fp:
        text = fp.read().strip()
    assert text == 'new'

    shutil.rmtree('test_diff')
    os.remove('test_config.cfg')
    os.remove('test_pa.bval')
    os.remove('test_pa.bvec')
    os.remove('test_ap.bval')
    os.remove('test_ap.bvec')
