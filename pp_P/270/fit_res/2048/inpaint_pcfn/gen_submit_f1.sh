#!/bin/bash

# 原始文件名称
original_file="./f1_inpaint_E.sh"

# 复制文件的数量
copies=99

for i in $(seq 0 $copies); do
    # 创建新文件的名称
    new_file="e_inp_$i.sh"

    # 复制原始文件到新文件
    cp $original_file $new_file

    # 在第10行替换文本
    sed -i "44s/number=\"0\"/number=\"$i\"/" $new_file
done

