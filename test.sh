#/data/predict/phantom_data/phantom_check/phantom_figure.py \
  #--apb0dir1 /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_20 \
  #--apb0dir2 /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_24 \
  #--padmridir /data/predict/phantom_data/ProNET_UCLA/dMRI_dir176_PA_22 \
  #--out test.png

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



/data/predict/phantom_data/phantom_check/phantom_figure.py \
    --mode dmri_b0 \
    --nifti_dirs apb0_1 pa_dmri apb0_2 \
    --names apb0_1 pa_dmri apb0_2 \
    --b0thr 5000 \
    --out_image new_test_nifti_dir_thr5000.png
