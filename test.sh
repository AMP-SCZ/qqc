#/data/predict/phantom_data/phantom_check/phantom_figure.py \
    #--mode dmri_b0 \
    #--dicom_dirs \
        #/data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_20 \
        #/data/predict/phantom_data/ProNET_UCLA/dMRI_dir176_PA_22 \
        #/data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_24 \
    #--names \
        #apb0_1 pa_dmri apb0_2 \
    #--out_image new_test.png



#/data/predict/phantom_data/phantom_check/phantom_figure.py \
    #--mode dmri_b0 \
    #--dicom_dirs \
        #/data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_20 \
        #/data/predict/phantom_data/ProNET_UCLA/dMRI_dir176_PA_22 \
        #/data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_24 \
        #/data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_20 \
    #--names \
        #apb0_1 pa_dmri apb0_2 dup \
    #--out_image new_test_dup.png


#/data/predict/phantom_data/phantom_check/phantom_figure.py \
    #--mode dmri_b0 \
    #--dicom_dirs \
        #/data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_20 \
        #/data/predict/phantom_data/ProNET_UCLA/dMRI_dir176_PA_22 \
        #/data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_24 \
        #/data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_20 \
    #--names \
        #apb0_1 pa_dmri apb0_2 dup \
    #--store_nifti \
    #--out_image new_test_dup.png


#/data/predict/phantom_data/phantom_check/phantom_figure.py \
    #--mode dmri_b0 \
    #--nifti_dirs apb0_1 pa_dmri apb0_2 \
    #--names apb0_1 pa_dmri apb0_2 \
    #--out_image new_test_nifti_dir.png



#/data/predict/phantom_data/phantom_check/phantom_figure.py \
    #--mode dmri_b0 \
    #--nifti_dirs apb0_1 pa_dmri apb0_2 \
    #--names apb0_1 pa_dmri apb0_2 \
    #--b0thr 5000 \
    #--out_image new_test_nifti_dir_thr5000.png


./phantom_figure.py \
    --mode dmri_b0 \
    --dicom_dirs \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_20 \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_dir176_PA_22 \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_24 \
    --names \
        apb0_1 pa_dmri apb0_2 \
    --store_nifti \
    --out_image b0_summary.png

./dicom_header_comparison.py \
    --json_files \
        apb0_1/apb0_1.json \
        pa_dmri/pa_dmri.json \
        apb0_2/apb0_2.json \
    --save_excel json_summary.xlsx
