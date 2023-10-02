import csv
from pathlib import Path

import nibabel as nib
import numpy as np

mri_root = Path("/data/predict1/data_from_nda/MRI_ROOT")
qqc = mri_root / "derivatives" / "quick_qc"

import sys

sys.path.append("/data/predict1/home/nick/anonymous_subses")
from test_nifti_bval_bvec_paths import test_bval_path, test_bvec_path, test_nifti_path


def create_dwi_pa_dict_of_dicts(mri_root):
    # Establish list of dwi pa nifti, bval, and bvec paths in mri_root
    dwi_pa_nifti_paths = list(
        mri_root.glob(
            "rawdata/sub-*/ses-*/dwi/sub-*_ses-*_acq-*_dir-PA_run-*_dwi.nii.gz"
        )
    )
    dwi_pa_bval_paths = list(
        mri_root.glob("rawdata/sub-*/ses-*/dwi/sub-*_ses-*_acq-*_dir-PA_run-*_dwi.bval")
    )
    dwi_pa_bvec_paths = list(
        mri_root.glob("rawdata/sub-*/ses-*/dwi/sub-*_ses-*_acq-*_dir-PA_run-*_dwi.bvec")
    )

    # {File name excluding suffix: {nifti, bval, or bvec: path}}
    dwi_pa_dict_of_dicts = {}

    for path in dwi_pa_nifti_paths:
        key = path.stem.split(".")[0]  # Remove suffix
        dwi_pa_dict_of_dicts[key] = {"nifti": path}  # Create new entry

    for path in dwi_pa_bval_paths:
        key = path.stem.split(".")[0]  # Remove suffix
        if key in dwi_pa_dict_of_dicts:
            dwi_pa_dict_of_dicts[key]["bval"] = path  # Add to existing entry
        else:
            print(f"Key non-match: {key}")
            dwi_pa_dict_of_dicts[key] = {"bval": path}  # Create new entry

    for path in dwi_pa_bvec_paths:
        key = path.stem.split(".")[0]  # Remove suffix
        if key in dwi_pa_dict_of_dicts:
            dwi_pa_dict_of_dicts[key]["bvec"] = path  # Add to existing entry
        else:
            print(f"Key non-match: {key}")
            dwi_pa_dict_of_dicts[key] = {"bvec": path}  # Create new entry

    # Find file names excluding suffix that lack a nifti, bval, or bvec
    keys_to_remove = []
    for outer_key, inner_dict in dwi_pa_dict_of_dicts.items():
        missing_keys = [
            key for key in ["nifti", "bval", "bvec"] if key not in inner_dict
        ]
        if missing_keys:
            print(
                f"No accompanying {' or '.join(missing_keys)} for {outer_key}. Removing from dictionary."
            )
            keys_to_remove.append(outer_key)

    # Remove them from dictionary
    for key in keys_to_remove:
        dwi_pa_dict_of_dicts.pop(key)

    # Transform outer keys to sub-*/ses-*
    dwi_pa_dict_of_dicts = {
        f"{key.split('_')[0]}/{key.split('_')[1]}": value
        for key, value in dwi_pa_dict_of_dicts.items()
    }

    return dwi_pa_dict_of_dicts


def extract_mean_volume_intensities(nifti_path, bval_path, bvec_path, subses=None):
    # Load nifti, bval, and bvec arrays
    nifti_array = nib.load(nifti_path).get_fdata()
    bval_array = np.loadtxt(bval_path)
    bvec_array = np.loadtxt(bvec_path)

    # Sanity check – Comparing number of nifti volumes against number of bvals and bvecs
    number_of_nifti_volumes = nifti_array.shape[3]
    number_of_bvals = len(bval_array)
    number_of_bvecs = bvec_array.shape[1]

    if number_of_nifti_volumes != number_of_bvals:
        raise ValueError(
            f"Mismatch: {number_of_nifti_volumes} nifti volumes and {number_of_bvals} bvals."
        )

    if number_of_nifti_volumes != number_of_bvecs:
        raise ValueError(
            f"Mismatch: {number_of_nifti_volumes} nifti volumes and {number_of_bvecs} bvecs."
        )

    # Initialize empty array to store mean volume intensities
    mean_volume_intensities = np.zeros(number_of_nifti_volumes)

    # Calculate mean volume intensities
    for volume in range(number_of_nifti_volumes):
        intensities = nifti_array[..., volume]
        mean_intensity = np.mean(intensities)
        mean_volume_intensities[volume] = mean_intensity

    # Sanity check – Checking that highest mean volume intensity is from a volume with bval <= 50
    highest_mean_volume_intensity_index = np.argmax(mean_volume_intensities)

    if bval_array[highest_mean_volume_intensity_index] > 50:
        warning_msg = f"Warning: The highest mean volume intensity is from a volume with bval of ({bval_array[highest_mean_volume_intensity_index]})"
        if subses is not None:
            warning_msg += f" for {subses}."
        print(warning_msg)

    # Return mean volume intensity array
    return mean_volume_intensities


def collect_mean_volume_intensities():
    # Establish dwi pa in mri_root {File name excluding suffix: {nifti, bval, and bvec: path}}
    dwi_pa_dict_of_dicts = create_dwi_pa_dict_of_dicts(mri_root)

    # Initialize empty dictionary to store mean volume intensities for all sub-*/ses-*
    pa_mean_volume_intensities_all_subses = {}

    # Loop through subses in dictionary
    for subses, inner_dict in dwi_pa_dict_of_dicts.items():
        path = qqc / subses / "dwi_pa_mean_volume_intensities.txt"

        # Load dwi_pa_mean_volume_intensities.txt if it exists on server
        if path.exists():
            pa_mean_volume_intensities_for_subses = np.loadtxt(path)
        else:
            try:
                # Save dwi_pa_mean_volume_intensities.txt if it does not exist on server
                pa_mean_volume_intensities_for_subses = extract_mean_volume_intensities(
                    inner_dict.get("nifti", "default_nifti_path"),
                    inner_dict.get("bval", "default_bval_path"),
                    inner_dict.get("bvec", "default_bvec_path"),
                    subses,
                )
            except IndexError as e:
                print(
                    f"IndexError occurred in extract_mean_volume_intensities for {subses}"
                )
                raise e
                # np.savetxt(path, pa_mean_volume_intensities_for_subses)

        # Appendto all subses mean volume intensities dictioanry
        pa_mean_volume_intensities_all_subses[
            subses
        ] = pa_mean_volume_intensities_for_subses


def test_extract_mean_volume_intensities():
    mean_volume_intensities_test = extract_mean_volume_intensities(
        test_nifti_path, test_bval_path, test_bvec_path
    )
    return mean_volume_intensities_test


def test_collect_mean_volume_intensities():
    collect_mean_volume_intensities_test = test_collect_mean_volume_intensities()
    return collect_mean_volume_intensities_test


def dict_to_csv(file_path, data_dict):
    with open(file_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        for key, value in data_dict.items():
            writer.writerow([key, value])
