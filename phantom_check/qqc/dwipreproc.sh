runQuickTopupEddy() {
    # run quick topup and eddy on the human pilot scan of the U24 data
    # currently, the function uses all the b0 images from the main DWI, as
    # well as the two ap b0 files -> this may needs to be configured later
    dwi_dir=$1
    session_dir=`dirname ${dwi_dir}`
    session=`basename ${session_dir}`
    subject_dir=`dirname ${session_dir}`
    subject=`basename ${subject_dir}`

    data_dir=${dwi_dir}
    out_dir_root=$2
    out_dir=${out_dir_root}/${subject}/${session}
    echo ${subject}
    echo ${session}
    echo ${data_dir}

    if [ ! -d ${out_dir} ]
    then
        mkdir -p ${out_dir}
    fi

    # extract b0 from the main PA image
    num=0
    bval_nums=''
    for bval in `cat ${data_dir}/*dir-PA_run-1_dwi.bval`
    do
        echo $bval
        if [ ${bval} -lt 50 ]
        then
            bval_nums=`echo ${bval_nums} ${num}`
        fi
        num=`expr ${num} + 1`
    done

    for bval_num in ${bval_nums}
    do
        echo ${bval_num}
        fslroi ${data_dir}/*dir-PA_run-1_dwi.nii.gz ${out_dir}/pa_b0_${bval_num} \
            ${bval_num} 1
    done
    
    #fslmerge -t ${out_dir}/pa_b0_merged ${out_dir}/pa_b0_[0123456789]*nii.gz

    #for testing purposes, just use the first b0
    fslmerge -t ${out_dir}/pa_b0_merged ${out_dir}/pa_b0_0.nii.gz

    # merge all b0s
    # there could be non-b0 included in the AP b0 as well
    run=1
    for ap_bval_file in ${data_dir}/*dir-AP_run-*dwi.bval
    do
        ap_num=0
        for ap_bval_num in `cat ${ap_bval_file}`
        do
            if [ ${ap_bval_num} -lt 50 ]
            then
                echo fslroi ${ap_bval_file%.bval}.nii.gz ${out_dir}/ap_b0_${run}_${ap_num} ${ap_num} 1
                fslroi ${ap_bval_file%.bval}.nii.gz ${out_dir}/ap_b0_${run}_${ap_num} ${ap_num} 1
            fi
            ap_num=`expr ${ap_num} + 1`
        done
        run=`expr ${run} + 1`
    done

    #fslmerge -t ${out_dir}/pa_ap_ap_b0_merged \
        #${out_dir}/pa_b0_merged.nii.gz \
        #${out_dir}/ap_b0_*.nii.gz

    # for testing purposes, just use the first b0
    fslmerge -t ${out_dir}/pa_ap_ap_b0_merged \
        ${out_dir}/pa_b0_merged.nii.gz \
        ${out_dir}/ap_b0_1_0.nii.gz \
        ${out_dir}/ap_b0_2_0.nii.gz


    rm ${out_dir}/acqparams.txt
    for bval_num in ${bval_nums}
    do
        printf "0 -1 0 0.0646\n" >> ${out_dir}/acqparams.txt
    done

    for ap_bval_file in ${data_dir}/*dir-AP_run-*dwi.bval
    do
        for ap_bval_num in `cat ${ap_bval_file}`
        do
            if [ ${ap_bval_num} -lt 50 ]
            then
                printf "0 1 0 0.0646\n" >> ${out_dir}/acqparams.txt
            fi
        done
    done

    printf "0 -1 0 0.0646\n0 -1 0 0.0646\n0 -1 0 0.0646" > ${out_dir}/acqparams.txt
    echo "Topup start"


    if [ ! -e ${out_dir}/hifi_b0.nii.gz ]
    then
        topup \
            --imain=${out_dir}/pa_ap_ap_b0_merged.nii.gz \
            --datain=${out_dir}/acqparams.txt \
            --config=b02b0_1.cnf \
            --out=${out_dir}/topup_results \
            --iout=${out_dir}/hifi_b0
    fi
    echo "Topup completed"

    fslmaths ${out_dir}/hifi_b0 -Tmean ${out_dir}/hifi_b0_avg
    bet ${out_dir}/hifi_b0_avg ${out_dir}/nodif_brain -m

    dwi=`ls ${data_dir}/*-PA_run-1_dwi.nii.gz`
    bval=`ls ${data_dir}/*-PA_run-1_dwi.bval`
    bvec=`ls ${data_dir}/*-PA_run-1_dwi.bvec`
    mask=${out_dir}/nodif_brain_mask.nii.gz

    # eddy
    indx=""
    for ((i=1; i<=${num}; i+=1)); do indx="$indx 1"; done
    echo $indx > ${out_dir}/index.txt

    echo "0 -1 0 0.0646" > ${out_dir}/eddy_acqp.txt

    #bsub -q pri_pnl -n 8 -o bsub.out -e bsub.err \
    echo "Eddy start"

    if [ ! -e ${out_dir}/eddy_out.nii.gz ]
    then
        eddy_openmp --imain=${dwi} \
                        --mask=${mask} \
                        --acqp=${out_dir}/eddy_acqp.txt \
                        --index=${out_dir}/index.txt \
                        --bvecs=${bvec} \
                        --bvals=${bval} \
                        --data_is_shelled \
                        --topup=${out_dir}/topup_results \
                        --repol \
                        --out=${out_dir}/eddy_out
    fi

    cp ${out_dir}/eddy_out.eddy_rotated_bvecs ${out_dir}/eddy_out.bvec
    cp ${bval} ${out_dir}/eddy_out.bval

    echo "Eddy completed"

    echo "Eddy QC"
    eddy_squeeze \
        --eddy_directories ${out_dir} \
        -od /data/predict/kcho/flow_test/MRI_ROOT/derivatives/eddy_qc \
        -sh -pt
}

export -f runQuickTopupEddy

dwi_dir=$1
out_dir_root=$2

session_dir=`dirname ${dwi_dir}`
session=`basename ${session_dir}`
subject_dir=`dirname ${session_dir}`
subject=`basename ${subject_dir}`

echo ${subject} ${session}
if [ ! -e ${out_dir_root}/${subject}/${session}/eddy_out.nii.gz ]
then
    echo Running quick DWI preproc on ${dwi_nifti_dir}
    runQuickTopupEddy ${dwi_nifti_dir} ${out_dir_root}
fi
