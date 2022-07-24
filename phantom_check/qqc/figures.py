from pathlib import Path
from phantom_check.utils.files import get_diffusion_data_from_nifti_prefix, \
        get_nondmri_data, load_data_bval
from phantom_check.utils.visualize import create_b0_signal_figure, \
        create_image_signal_figure 
import sys
sys.path.append('/data/predict/phantom_data/softwares/nifti-snapshot')
from nifti_snapshot import nifti_snapshot



def quick_figures(subject_dir: Path, outdir: Path):
    # quick figures
    # b0 signal
    fig_num_in_row = 3

    if not (outdir / '07_summary_b0.png').is_file():
        dwi_dir = subject_dir / 'dwi'
        threshold = 50
        dataset = []
        for nifti_path in dwi_dir.glob('*.nii.gz'):
            if 'sbref' not in nifti_path.name:
                nifti_prefix = nifti_path.parent / nifti_path.name.split('.')[0]
                data, bval_arr = get_diffusion_data_from_nifti_prefix(
                        nifti_prefix, '', threshold, False)
                dataset.append((data, bval_arr,
                                nifti_prefix.name.split('ses-')[1]))

        create_b0_signal_figure(dataset, outdir / '07_summary_b0.png',
                                True, fig_num_in_row, wide_fig=False)


    if not (outdir / '08_summary_dwi.png').is_file():
        dwi_dir = subject_dir / 'dwi'
        dataset = []
        for nifti_path in dwi_dir.glob('*.nii.gz'):
            if 'sbref' not in nifti_path.name:
                nifti_prefix = nifti_path.parent / nifti_path.name.split('.')[0]
                data, _ = load_data_bval(nifti_prefix)
                dataset.append((data, nifti_prefix.name.split('ses-')[1]))

        create_image_signal_figure(dataset, outdir / '08_summary_dwi.png',
                                True, fig_num_in_row, wide_fig=False)


    if not (outdir / '09_summary_fmri.png').is_file():
        fmri_dir = subject_dir / 'func'
        dataset = []
        for nifti_path in fmri_dir.glob('*.nii.gz'):
            if 'sbref' not in nifti_path.name:
                nifti_prefix = nifti_path.parent / nifti_path.name.split('.')[0]
                data = get_nondmri_data(nifti_prefix, 'nifti_prefix', '', False)
                dataset.append((data, nifti_prefix.name.split('ses-')[1]))

        create_image_signal_figure(dataset, outdir / '09_summary_fmri.png',
                                True, 4, wide_fig=True)


    anat_dir = subject_dir / 'anat'
    for nifti_path in anat_dir.glob('*.nii.gz'):
        outname = nifti_path.name.split('.nii.gz')[0] + '.png'
        if not (outdir / outname).is_file():
            fig = nifti_snapshot.SimpleFigure(
                image_files = [nifti_path],
                title = nifti_path.name,
                make_transparent_zero = True,
                cbar_width = 0.5,
                cbar_title = 'Intensity',
                output_file = outdir / outname,
            )

    # add dMRI & fMRI visualization
    dwi_dir = subject_dir / 'dwi'
    for nifti_path in dwi_dir.glob('*.nii.gz'):
        outname = nifti_path.name.split('.nii.gz')[0] + '.png'
        if not (outdir / outname).is_file():
            fig = nifti_snapshot.SimpleFigure(
                image_files = [nifti_path],
                title = nifti_path.name,
                make_transparent_zero = True,
                volumes=[0],
                cbar_width = 0.5,
                cbar_title = 'Intensity',
                output_file = outdir / outname,
            )

    # add dMRI & fMRI visualization
    func_dir = subject_dir / 'func'
    for nifti_path in func_dir.glob('*.nii.gz'):
        outname = nifti_path.name.split('.nii.gz')[0] + '.png'
        if not (outdir / outname).is_file():
            fig = nifti_snapshot.SimpleFigure(
                image_files = [nifti_path],
                title = nifti_path.name,
                make_transparent_zero = True,
                volumes=[0],
                cbar_width = 0.5,
                cbar_title = 'Intensity',
                output_file = outdir / outname,
            )

