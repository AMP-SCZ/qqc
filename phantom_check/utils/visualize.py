from typing import List
import tempfile
import shutil
from pathlib import Path
from phantom_check.utils.files import convert_to_img
import nibabel as nb
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd


def print_diff_shared(title: str, df: pd.DataFrame) -> None:
    print(title)
    print('='*80)
    # pretty_print_dict(diff_items)
    print(df)
    print()
    print()
    print('='*80)
    print()


def get_jsons_from_dicom_dirs(dicom_dirs: List[str],
                              names: List[str] = None,
                              save_outputs: bool = True):
    json_files = []
    for num, dicom_dir in enumerate(dicom_dirs):
        name = names[num] if names else Path(dicom_dir).name
        temp_dir = tempfile.TemporaryDirectory()
        convert_to_img(dicom_dir, temp_dir.name, name)
        json_files.append(Path(temp_dir) / (name + '.json'))

        if save_outputs:
            shutil.copytree(temp_dir.name, name)

        temp_dir.cleanup()

    return json_files


def create_b0_signal_figure_prev(data1: np.array, data1_bval: np.array,
                            data2: np.array, data2_bval: np.array,
                            data3: np.array, data3_bval: np.array,
                            out: str, savefig: bool = False):
    '''Plot b0 summary from three different 4d dMRI volumes

    Key arguments:
        data1: first AP B0 volumes
        data2: second AP B0  volumes
        data3: b0 volumes extracted from the PA dMRI
        out: output image file name, eg) test.png
        savefig: save figure if True
    '''
    fig, axes = plt.subplots(ncols=3, figsize=(12, 8), dpi=150)

    for ax, (data, bval, name, color) in zip(
            np.ravel(axes),
            [(data1, data1_bval, 'b0 AP 1', 'b'),
             (data3, data3_bval, 'b0 PA dMRI', 'r'),
             (data2, data2_bval, 'b0 AP 2', 'b')]):
        data_mean = [data[:, :, :, vol_num].mean() for vol_num in
                np.arange(data.shape[-1])]
        ax.plot(data_mean, color+'-')
        ax.plot(data_mean, color+'o')
        ax.set_ylabel("Average signal in all voxels")
        ax.set_xlabel("B value")
        ax.set_title(name)
        ax.set_xticks(np.arange(len(bval)))
        ax.set_xticklabels(bval)

    max_y = 0
    min_y = 100000
    for x in data1, data2, data3:
        values = np.array(
                [x[:, :, :, vol_num].mean() for vol_num
                    in np.arange(x.shape[-1])])
        max_y = values.max() if values.max() > max_y else max_y
        min_y = values.min() if values.min() < min_y else min_y

    for ax in axes:
        ax.set_ylim(min_y-5, max_y+5)

    fig.subplots_adjust(wspace=0.3, hspace=0.3)

    if savefig:
        fig.savefig(out)
    else:
        return fig


def create_image_signal_figure(dataset: List[tuple], out: str,
                               savefig: bool = False, col_num: int = 3, 
                               wide_fig: bool = False):
    '''Plot b0 summary from three different 4d dMRI volumes

    Key arguments:
        dataset: Tuple of (data, name), tuple.
        out: output image file name, eg) test.png, str.
        savefig: save figure if True, bool.
        col_num: number of figures in a single row, int.
        wide_fig: option to create horizontally long figure, bool.
    '''
    col_width = 4
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

    color_num = 0
    for ax, (data, name) in zip(np.ravel(axes), dataset):
        color = cm(1.*color_num/len(dataset))
        data_mean = [data[:, :, :, vol_num].mean() for vol_num in
                np.arange(data.shape[-1])]
        ax.plot(data_mean, color=color, linestyle='-', marker='o')
        ax.set_ylabel("Average signal in all voxels")
        ax.set_xlabel("Volume")
        ax.set_title(name)
        color_num += 1

    max_y = 0
    min_y = 100000
    for data in [x[0] for x in dataset]:
        values = np.array(
                [data[:, :, :, vol_num].mean() for vol_num
                    in np.arange(data.shape[-1])])
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


def create_b0_signal_figure(dataset: List[tuple], out: str,
                            savefig: bool = False, col_num: int = 3, 
                            wide_fig: bool = False):
    '''Plot b0 summary from three different 4d dMRI volumes

    Key arguments:
        data1: first AP B0 volumes
        data2: second AP B0  volumes
        data3: b0 volumes extracted from the PA dMRI
        out: output image file name, eg) test.png
        savefig: save figure if True
    '''
    col_width = 4
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

    color_num = 0
    for ax, (data, bval, name) in zip(np.ravel(axes), dataset):
        color = cm(1.*color_num/len(dataset))
        data_mean = [data[:, :, :, vol_num].mean() for vol_num in
                np.arange(data.shape[-1])]
        ax.plot(data_mean, color=color, linestyle='-', marker='o')
        ax.set_ylabel("Average signal in all voxels")
        ax.set_xlabel("B0 value")
        ax.set_title(name)
        ax.set_xticks(np.arange(len(bval)))
        ax.set_xticklabels(bval)
        color_num += 1

    max_y = 0
    min_y = 100000
    for data in [x[0] for x in dataset]:
        values = np.array(
                [data[:, :, :, vol_num].mean() for vol_num
                    in np.arange(data.shape[-1])])
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


