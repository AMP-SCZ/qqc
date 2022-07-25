from typing import List
import tempfile
import shutil
from pathlib import Path
from qqc.utils.files import convert_to_img
import nibabel as nb
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.gridspec as gridspec

import seaborn as sns



def print_diff_shared(title: str, df: pd.DataFrame) -> None:
    print(title)
    print('='*80)
    # pretty_print_dict(diff_items)
    # if df.shape[1] > 0:
    if len(df) > 0:
        # sort df by name of the json_file if there is "_\d?" pattern
        try:
            df['series_num'] = df.index.str.extract(
                    r'_(\d{1,2})').values.astype(int)
            df.sort_values(by='series_num', inplace=True, ascending=True)
            df.drop('series_num', axis=1, inplace=True)
        except:
            pass
        print(df)
    else:
        print('No difference')
    print('='*80)
    print('\n\n')


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



def plot_anat_jsons_from_mriqc(df: pd.DataFrame) -> None:
    '''Plot anat jsons from mriqc'''
    df_melt = pd.melt(df.reset_index(), id_vars=['index', 'labels'],
                      var_name='subject')

    g = sns.catplot(x='index', y='value', hue='subject',
                    sharex=False, sharey=False,
                    data=df_melt)

    g.fig.set_size_inches(15, 10)
    g.fig.set_dpi(150)
    g.ax.tick_params(axis='x', rotation=90)
    g.ax.set_ylabel('QC Value provided by MRIQC - Normalized')

    g.fig.subplots_adjust(bottom=0.2)
    g.fig.savefig('tmp.png')

    return


def plot_anat_jsons_from_mriqc_with_opendata(
        df: pd.DataFrame, out_image: str) -> None:
    '''Plot anat jsons from mriqc'''

    # open_data
    df_melt = pd.melt(
            df.T[df.T['source'] == 'opendata'].drop(
                'source', axis=1).T.reset_index(),
            id_vars=['index'],
            var_name='subject')

    # mriqc data
    df_mri_qc_melt = pd.melt(
            df.T[df.T['source'] == 'mriqc'].drop(
                'source', axis=1).T.reset_index(),
            id_vars=['index'],
            var_name='subject')

    # plot box plots
    g = sns.catplot(x='index', y='value',
                    col='index', col_wrap=10,
                    sharex=False, sharey=False,
                    kind='box',
                    data=df_melt)

    # set boxplot transparency
    for ax in np.ravel(g.axes):
        alpha = 0.1

        a = ax.get_lines()
        for i in a:
            i.set_alpha(alpha+1)

        for patch in ax.artists:
            # patch
            patch.set_alpha(0.1)
            red, green, blue, _ = patch.get_facecolor()
            patch.set_facecolor((red, green, blue, alpha))

            # edge
            red, green, blue, _ = patch.get_edgecolor()
            patch.set_edgecolor((red, green, blue, alpha))


    # add mriqc data points (as points)
    for num, ax in enumerate(np.ravel(g.axes)):
        index = ax.get_title().split(' = ')[1]
        df_tmp = df_mri_qc_melt.groupby('index').get_group(index)
        df_tmp = df_tmp[df_tmp['subject'] != 'labels']

        # for each measure
        for index, row in df_tmp.iterrows():
            # ylim adjust if needed
            ylim_range = ax.get_ylim()
            if row['value'] < ylim_range[0]:
                ax.set_ylim(row['value'], ylim_range[1])

            if row['value'] > ylim_range[1]:
                ax.set_ylim(ylim_range[0], row['value'])

            # plot for each subject
            ax.plot(0, row['value'], 'o',
                    alpha=0.9, label=row['subject'])

        # store an example point set for the legend
        if num == 0:
            handles, labels = ax.get_legend_handles_labels()

        ax.set_title('')

    # figure settings
    g.fig.set_size_inches(15, 15)
    g.fig.set_dpi(150)

    # legend ax
    legend_ax = g.fig.add_axes([0.95, 0.1, 0.01, 0.01])
    legend_ax.axis('off')
    legend_ax.legend(handles, labels, loc='best')

    # subplots position adjust
    g.fig.subplots_adjust(wspace=0.25, hspace=0.25,
                          bottom=0.05, top=0.95, left=0.08, right=0.95)

    g.fig.suptitle(
            f'MRIQC summary overlaid on top of normative (3T) qc measures '
            f'(n={len(df_melt.subject.unique())})')

    g.fig.savefig(out_image)

    return
