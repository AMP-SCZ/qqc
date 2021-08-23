 wget <dropbox_link>

#unzip
unzip <zip file>


data_dir=/data/predict/phantom_data/ProNET_WashU_Prisma/phantom/data/nifti

# convert all dicoms
for i in ${data_dir}/*
do
    name=`basename ${i}`
    mkdir /data/predict/phantom_data/ProNET_WashU_Prisma/human_pilot/data/nifti/${name}
    dcm2niix -b y -z y -f %d_%s -d 9 -o /data/predict/phantom_data/ProNET_WashU_Prisma/human_pilot/data/nifti/${name} ${i}
done


# compare data against phantom data
for i in ${data_dir}/*
do 
   name=`basename ${i}`
   name_without_number=${name%_[[:digit:]]*}
   /data/predict/phantom_data/softwares/phantom_check/dicom_header_comparison.py \
       --json_files  \
       T1w_MPR_10/T1w_MPR_10.json \
          /data/predict/phantom_data/human_test/human_subject_UCLA/T1w_MPR_10/T1w_MPR_10.json \
       --print_diff
done


# compare dMRI_b0_AP_20 bvals
/data/predict/phantom_data/softwares/phantom_check/dwi_extra_comparison.py \
        --bval_files \
            /data/predict/phantom_data/human_test/human_subject_UCLA/dMRI_b0_AP_20/dMRI_b0_AP_20.bval \
            dMRI_b0_AP_20/dMRI_b0_AP_20.bval \

# compare dMRI_b0_AP_24 bvals
/data/predict/phantom_data/softwares/phantom_check/dwi_extra_comparison.py \
        --bval_files \
            /data/predict/phantom_data/human_test/human_subject_UCLA/dMRI_b0_AP_24/dMRI_b0_AP_24.bval \
            dMRI_b0_AP_24/dMRI_b0_AP_24.bval \

# compare dMRI_dir176_PA_22 bvals
/data/predict/phantom_data/softwares/phantom_check/dwi_extra_comparison.py \
        --bval_files \
            /data/predict/phantom_data/human_test/human_subject_UCLA/dMRI_dir176_PA_22/dMRI_dir176_PA_22.bval \
            dMRI_dir176_PA_22/dMRI_dir176_PA_22.bval \


# summarize dMRI b0 signal
/data/predict/phantom_data/softwares/phantom_check/phantom_figure.py \
    --mode dmri_b0 \
    --nifti_dirs \
        dMRI_b0_AP_20 \
        dMRI_b0_AP_24 \
        dMRI_dir176_PA_22 \
    --names \
        dMRI_b0_AP_20 \
        dMRI_b0_AP_24 \
        dMRI_dir176_PA_22 \
    --store_nifti \
    --out_image diffusion_b0_summary.png


# summarize all dMRI signal
/data/predict/phantom_data/softwares/phantom_check/phantom_figure.py \
   --mode dmri_b0 \
   --nifti_dirs \
       dMRI_b0_AP_20 \
       dMRI_b0_AP_24 \
       dMRI_dir176_PA_22 \
   --names \
       dMRI_b0_AP_20 \
       dMRI_b0_AP_24 \
       dMRI_dir176_PA_22 \
   --b0thr 5000 \
   --wide_fig \
   --out_image diffusion_signal_summary.png


# summarize fMRI signal
/data/predict/phantom_data/softwares/phantom_check/phantom_figure.py \
   --mode fmri \
   --nifti_dirs \
       rfMRI_REST_AP_16 \
       rfMRI_REST_PA_18 \
       rfMRI_REST_AP_28 \
       rfMRI_REST_PA_30 \
   --names \
       rfMRI_REST_AP_16 \
       rfMRI_REST_PA_18 \
       rfMRI_REST_AP_28 \
       rfMRI_REST_PA_30 \
   --store_nifti \
   --fig_num 4 \
   --wide_fig \
   --out_image fmri_signal_summary.png


# see if there is a difference between dMRI protocols
/data/predict/phantom_data/softwares/phantom_check/dicom_header_comparison.py \
   --json_files  \
       dMRI_b0_AP_20/dMRI_b0_AP_20.json \
       dMRI_b0_AP_24/dMRI_b0_AP_24.json \
       dMRI_dir176_PA_22/dMRI_dir176_PA_22.json \
   --save_excel difference_between_dmri_protocol.xlsx

# see if there is a difference between fMRI protocols
/data/predict/phantom_data/softwares/phantom_check/dicom_header_comparison.py \
   --json_files  \
       rfMRI_REST_AP_16/rfMRI_REST_AP_16.json \
       rfMRI_REST_PA_18/rfMRI_REST_PA_18.json \
       rfMRI_REST_AP_28/rfMRI_REST_AP_28.json \
       rfMRI_REST_PA_30/rfMRI_REST_PA_30.json \
   --save_excel difference_between_fmri_protocol.xlsx
