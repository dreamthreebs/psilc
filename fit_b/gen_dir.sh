old_fold="benchmark_T_95GHz_3sigma"
new_fold="PowerSpectrumTest_95_GHz"
mkdir -p ./$new_fold
mkdir -p ./$new_fold/inpainting
mkdir -p ./$new_fold/fit_res
mkdir -p ./$new_fold/mask

cp ./$old_fold/* ./$new_fold
cp ./$old_fold/inpainting/* ./$new_fold/inpainting
cp ./$old_fold/fit_res/* ./$new_fold/fit_res
cp ./$old_fold/mask/* ./$new_fold/mask


