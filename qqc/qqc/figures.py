import numpy as np
import nibabel as nb
from pathlib import Path
from qqc.utils.files import get_diffusion_data_from_nifti_prefix, \
        get_nondmri_data, load_data_bval, get_subject_session_from_input_dir
from qqc.utils.visualize import create_b0_signal_figure, \
        create_image_signal_figure
from qqc.qqc.smoothness import summary_smoothness_table_for_a_session

import sys
sys.path.append('/data/predict1/home/kcho/nifti-snapshot')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from nifti_snapshot import nifti_snapshot
import seaborn as sns

import logging
logger = logging.getLogger(__name__)


def quick_figures(subject_dir: Path, outdir: Path):
    # quick figures
    # b0 signal
    fig_num_in_row = 3

    plt.style.use('default')
    if not (outdir / '07_summary_b0.png').is_file():
        dwi_dir = subject_dir / 'dwi'
        threshold = 50
        dataset = []
        for nifti_path in dwi_dir.glob('*.nii.gz'):
            if 'sbref' not in nifti_path.name:
                nifti_prefix = nifti_path.parent / nifti_path.name.split('.')[0]
                try:
                    data, bval_arr = get_diffusion_data_from_nifti_prefix(
                            nifti_prefix, '', threshold, False)
                except IndexError:
                    logger.warning('bval mismatch')
                    continue
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

        # multiple axes figure
        # create_image_signal_figure(dataset, outdir / '09_summary_fmri.png',
                                # True, 4, wide_fig=True)

        # single ax figure
        create_image_signal_figure(
                dataset, outdir / '09_summary_fmri.png',
                True, 1, wide_fig=False, flatten=True)


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

    # add 4d visualization
    dwi_dir = subject_dir / 'dwi'
    for nifti_path in dwi_dir.glob('*dwi.nii.gz'):
        outname = outdir / (nifti_path.name.split('.nii.gz')[0])
        if not (outdir / outname).is_file():
            fig = nifti_snapshot.SimpleFigureGif(
                image_files = [nifti_path],
                file_name_prefix = outname)

    func_dir = subject_dir / 'func'
    for nifti_path in func_dir.glob('*bold.nii.gz'):
        outname = outdir / (nifti_path.name.split('.nii.gz')[0])
        if not (outdir / outname).is_file():
            fig = nifti_snapshot.SimpleFigureGif(
                image_files = [nifti_path],
                file_name_prefix = outname)


def create_and_show_gif(dwi_pa_loc: Path, name_prefix: str = None) -> None:
    """
    Creates and shows a GIF animation from a DWI image file.

    Parameters:
    - dwi_pa_loc (Path): The path to the DWI image file.
    - name_prefix (str, optional): The prefix for the output file names.
        If not provided, the prefix will be the same as the input file name.

    Returns:
        None
    """
    dwi_pa_loc = Path(dwi_pa_loc)
    bval_file = dwi_pa_loc.parent / (dwi_pa_loc.name.split('.')[0] + '.bval')
    
    if name_prefix is None:
        name_prefix = dwi_pa_loc.name.split('.')[0]
    else:
        pass
        
    logger.info('Loading data')
    img = nb.load(dwi_pa_loc)
    data = img.get_fdata()
    bval_arr = np.round(np.loadtxt(bval_file), -2)

    # for unique b-shells
    for bval in np.unique(bval_arr):
        if bval > 1000:
            continue
        out_gif_name = f"{name_prefix}_b{bval}.gif"
        data_bval = data[..., np.where(bval_arr==bval)[0]]
        nb.Nifti1Image(
                data_bval, affine=img.affine, header=img.header).to_filename(
                        f"{name_prefix}_b{bval}.nii.gz")
        
        # Create a series of frames
        filenames = []
        for i in range(data_bval.shape[-1]):
            fig, axes = plt.subplots(ncols=3, nrows=3, figsize=(15, 15))

            slice_nums = np.linspace(0, data_bval.shape[-2]-1, 9).round(0)
            for slice_num, ax in zip(slice_nums, np.ravel(axes)):
                ax.imshow(data_bval[:, :, int(slice_num), i])

            # Save frame
            filename = f'frame_{i}.png'
            filenames.append(filename)
            fig.suptitle(f"dwi_pa_loc.name b{bval}")
        

            fig.savefig(filename)
            plt.close()
            # break

            
        with imageio.get_writer(out_gif_name, mode='I', duration=0.1) as writer:
            for filename in filenames:
                image = imageio.imread(filename)
                writer.append_data(image)

        # Clean-up frames
        for filename in filenames:
            os.remove(filename)

        # Display the GIF in Jupyter Notebook
        # from IPython.display import Image
        # return Image(filename=f"{n

def create_smoothness_figure(rawdata_dir, fig_out):
    subject, session = get_subject_session_from_input_dir(rawdata_dir)
    all_df = summary_smoothness_table_for_a_session(subject, session)
    all_df_melt = all_df.melt(
            id_vars=['name', 'subject', 'session',
                     'level', 'site', 'modality'],
            var_name='metric',
            value_name='value', value_vars=['FWHM', 'ACF'])
    plt.style.use('default')

    # main figure
    g = sns.catplot(data=all_df_melt, x='name', y='value',
                    row='metric', hue='level', kind='violin',
                    sharey=False, legend=False)

    g.fig.set_size_inches(20, 10)

    # label session's data with a red star
    x_offset = 0.27
    for ax in np.ravel(g.fig.axes):
        if len(ax.get_xticklabels()) > 0:
            x_labels = ax.get_xticklabels()

    handles, labels = g.axes[1, 0].get_legend_handles_labels()
    for ax in np.ravel(g.fig.axes):
        var = ax.get_title().split(' = ')[1]
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
        for i in x_labels:
            name = i.get_text()
            x, _ = i.get_position()
            ses_value = all_df[(all_df.level == f'{subject}/{session}') &
                               (all_df.name == name)][var]
            star_plot, = ax.plot(x-x_offset, ses_value, '*',
                                 color='red', markersize=10)
        ax.set_title(var)
        ax.set_ylabel(var)

    # add legend to the first ax
    ax = np.ravel(g.axes)[1]
    ax.legend([star_plot] + handles[1:],
            [f'{subject}/{session}', 'Site data', 'Study data'],
            loc='upper right', bbox_to_anchor=[0.96, 0.94, 0, 0])
    ax.set_xlabel('Series')
    g.fig.tight_layout()
    g.fig.savefig(fig_out)
    plt.close()
