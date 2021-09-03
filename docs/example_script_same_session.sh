script_location=/data/predict/phantom_data/softwares/phantom_check
export PYTHONPATH=$PYTHONPATH:${script_location}

cd /data/predict/phantom_data/ProNET_WashU_Prisma/phantom/data/nifti

# checking shim setting in scans from 13 - 24
${script_location}/scripts/dicom_header_comparison.py \
    --json_files \
        DistortionMap_AP_13/DistortionMap_AP_13.json \
        DistortionMap_PA_14/DistortionMap_PA_14.json \
        rfMRI_REST_AP_SBRef_15/rfMRI_REST_AP_SBRef_15.json \
        rfMRI_REST_AP_16/rfMRI_REST_AP_16.json \
        rfMRI_REST_PA_SBRef_17/rfMRI_REST_PA_SBRef_17.json \
        rfMRI_REST_PA_18/rfMRI_REST_PA_18.json \
        dMRI_b0_AP_SBRef_19/dMRI_b0_AP_SBRef_19.json \
        dMRI_b0_AP_20/dMRI_b0_AP_20.json \
        dMRI_dir176_PA_SBRef_21/dMRI_dir176_PA_SBRef_21.json \
        dMRI_dir176_PA_22/dMRI_dir176_PA_22.json \
        dMRI_b0_AP_SBRef_23/dMRI_b0_AP_SBRef_23.json \
        dMRI_b0_AP_24/dMRI_b0_AP_24.json \
    --field_specify ShimSetting \
    --print_diff \
    --print_shared


# checking shim setting in scans from 25 - 30
${script_location}/scripts/dicom_header_comparison.py \
    --json_files \
        DistortionMap_AP_25/DistortionMap_AP_25.json \
        DistortionMap_PA_26/DistortionMap_PA_26.json \
        rfMRI_AP_SBRef_27/rfMRI_REST_AP_SBRef_27.json \
        rfMRI_REST_AP_28/rfMRI_REST_AP_28.json \
        rfMRI_REST_PA_SBRef_29/rfMRI_REST_PA_SBRef_29.json \
        rfMRI_REST_PA_30/rfMRI_REST_PA_30.json \
    --field_specify ShimSetting \
    --print_diff \
    --print_shared


# checking image orientation in dMRI, fMRI and distortionMap
${script_location}/scripts/dicom_header_comparison.py \
    --json_files \
        DistortionMap_AP_13/DistortionMap_AP_13.json \
        dMRI_b0_AP_24/dMRI_b0_AP_24.json \
        rfMRI_REST_AP_28/rfMRI_REST_AP_28.json \
        DistortionMap_AP_25/DistortionMap_AP_25.json \
        dMRI_b0_AP_SBRef_19/dMRI_b0_AP_SBRef_19.json \
        rfMRI_REST_AP_SBRef_15/rfMRI_REST_AP_SBRef_15.json \
        DistortionMap_AP_7/DistortionMap_AP_7.json \
        dMRI_b0_AP_SBRef_23/dMRI_b0_AP_SBRef_23.json \
        rfMRI_REST_PA_18/rfMRI_REST_PA_18.json \
        DistortionMap_AP_8/DistortionMap_PA_8.json \
        dMRI_dir176_PA_22/dMRI_dir176_PA_22.json \
        rfMRI_REST_PA_SBRef_29/rfMRI_REST_PA_SBRef_29.json \
        DistortionMap_PA_14/DistortionMap_PA_14.json \
        dMRI_dir176_PA_SBRef_21/dMRI_dir176_PA_SBRef_21.json \
        rfMRI_REST_PA_30/rfMRI_REST_PA_30.json \
        DistortionMap_PA_26/DistortionMap_PA_26.json \
        rfMRI_AP_SBRef_27/rfMRI_REST_AP_SBRef_27.json \
        rfMRI_REST_PA_SBRef_17/rfMRI_REST_PA_SBRef_17.json \
        dMRI_b0_AP_20/dMRI_b0_AP_20.json \
        rfMRI_REST_AP_16/rfMRI_REST_AP_16.json \
    --field_specify ImageOrientationPatientDICOM \
    --print_diff \
    --print_shared


# checking image orientation in T1w and T2w
${script_location}/scripts/dicom_header_comparison.py \
    --json_files \
        T1w_MPR_9/T1w_MPR_9.json \
        T1w_MPR_10/T1w_MPR_10.json \
        T2w_SPC_11/T2w_SPC_11.json \
        T2w_SPC_12/T2w_SPC_12.json \
    --field_specify ImageOrientationPatientDICOM \
    --print_diff \
    --print_shared
