#!/bin/bash

# 原始文件名称
original_file="./calc_pcn_dl.py"

# 复制文件的数量
copies=99

for i in $(seq 1 $copies); do
    # 创建新文件的名称
    new_file="calc_pcn_dl_$i.py"

    # 复制原始文件到新文件
    cp $original_file $new_file

    # 在第10行替换文本
    sed -i "12s/rlz_idx = 0/rlz_idx = $i/" $new_file
done
