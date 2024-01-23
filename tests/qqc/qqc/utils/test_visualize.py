import math
import matplotlib.pyplot as plt
import numpy as np
from typing import List
from pathlib import Path
from qqc.utils.files import get_nondmri_data


def create_image_signal_figure(dataset: List[tuple], out: str,
                               savefig: bool = False, col_num: int = 3,
                               wide_fig: bool = False, flatten: bool = False):
    '''Plot b0 summary from three different 4d dMRI volumes

    Key arguments:
        dataset: Tuple of (data, name), tuple.
        out: output image file name, eg) test.png, str.
        savefig: save figure if True, bool.
        col_num: number of figures in a single row, int.
        wide_fig: option to create horizontally long figure, bool.
    '''
    col_width = 4

    if flatten:
        row_num = 1
    else:
        row_num = math.ceil(len(dataset) / col_num)

    row_height = 8
    width = len(dataset) * col_width
    height = row_num * row_height

    if wide_fig:
        fig, axes = plt.subplots(nrows=col_num, ncols=row_num,
                                 figsize=(height*2, width), dpi=150)
    else:
        fig, axes = plt.subplots(ncols=col_num, nrows=row_num,
                                 figsize=(width, height), dpi=150)

    # color
    cm = plt.get_cmap('brg')

    if flatten:
        color_num = 0
        ax = axes
        for data, name in dataset:
            color = cm(1.*color_num/len(dataset))
            data_mean = [data[:, :, :, vol_num].mean() for vol_num in
                         np.arange(data.shape[-1])]

            ax.plot(data_mean, label=name, color=color, linestyle='-', marker='o')
            ax.set_xlabel("Volume")
            color_num += 1
        ax.set_title('Average signal across volume')
        _ = ax.legend()

    else:
        color_num = 0
        for ax, (data, name) in zip(np.ravel(axes), dataset):
            color = cm(1.*color_num/len(dataset))
            data_mean = [data[:, :, :, vol_num].mean() for vol_num in
                         np.arange(data.shape[-1])]

            ax.plot(data_mean, label=name, color=color, linestyle='-', marker='o')
            ax.set_ylabel("Average signal in all voxels")
            ax.set_xlabel("Volume")

            ax.set_title(name)
            color_num += 1

    max_y = 0
    min_y = 100000
    for data in [x[0] for x in dataset]:
        values = np.array(
                [data[:, :, :, vol_num].mean() for vol_num in
                 np.arange(data.shape[-1])])
        max_y = values.max() if values.max() > max_y else max_y
        min_y = values.min() if values.min() < min_y else min_y

    for ax in np.ravel(axes):
        ax.set_ylim(min_y-5, max_y+5)

        if wide_fig:
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    for ax in np.ravel(axes)[len(dataset):]:
        ax.axis('off')

    fig.subplots_adjust(wspace=0.3, hspace=0.3)

    if savefig:
        fig.savefig(out)
    else:
        return fig


def test_quick_figures():
    subject_dir = Path('/data/predict1/home/kcho/MRI_site_cert/qqc_output/rawdata/sub-GW/ses-202311151')
    outdir = Path('.')

    fmri_dir = subject_dir / 'func'
    dataset = []
    for nifti_path in fmri_dir.glob('*.nii.gz'):
        if 'sbref' not in nifti_path.name:
            nifti_prefix = nifti_path.parent / nifti_path.name.split('.')[0]
            data = get_nondmri_data(nifti_prefix, 'nifti_prefix', '', False)
            dataset.append((data, nifti_prefix.name.split('ses-')[1]))

    create_image_signal_figure(
            dataset, outdir / '09_summary_fmri.png',
            True, 1, wide_fig=False, flatten=True)

    # create_image_signal_figure(dataset, outdir / '09_summary_fmri.png',
                               # True, 4, wide_fig=True)
