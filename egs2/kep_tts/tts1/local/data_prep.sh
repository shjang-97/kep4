#!/usr/bin/env bash

. ./path.sh || exit 1;
. ./cmd.sh || exit 1;

log() {
    local fname=${BASH_SOURCE[1]##*/}
    echo -e "$(date '+%Y-%m-%dT%H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
}

num_dev=50
num_eval=50
train_set="tr_no_dev"
dev_set="dev"
eval_set="eval1"
nj=32
threshold=35

db=$1
data_dir=$2
transcript=${db}/transcripts

# check arguments
if [ $# != 2 ]; then
    echo "Usage: $0 <db_root> <data_log_dir>"
    echo "e.g.: $0 /path/to/your_data data/train"
    exit 1
fi

set -euo pipefail

# check directory existence
# [ ! -e "${data_dir}" ] && mkdir -p "${data_dir}"  # 폴더 없으면 생성
[ -e "${data_dir}" ] && rm -r "${data_dir}" && mkdir -p "${data_dir}"  # 폴더 있으면 삭제 후 생성

train_data_dirs=""
dev_data_dirs=""
eval_data_dirs=""

# 스피커 ID 목록 (폴더 이름으로 구분)
# spks=$(find "${db}/wav24" -maxdepth 1 -exec basename {} \; | sort | grep -v wav24)
# 스피커 ID 목록 (폴더 이름으로 구분)
spks=$(find "${db}/wav24" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort -f)

for spk in ${spks}; do
    [ ! -e data/${spk}_train ] && mkdir -p data/${spk}_train

    # set filenames
    scp=data/${spk}_train/wav.scp
    utt2spk=data/${spk}_train/utt2spk
    text=data/${spk}_train/text
    segments=data/${spk}_train/segments
    spk2utt=data/${spk}_train/spk2utt

    # 파일 초기화
    [ -e "${scp}" ] && rm "${scp}"
    [ -e "${utt2spk}" ] && rm "${utt2spk}"
    [ -e "${text}" ] && rm "${text}"
    [ -e "${segments}" ] && rm "${segments}"
    [ -e "${spk2utt}" ] && rm "${spk2utt}"
 
    # 파일 하나씩 처리
    find "${db}/wav24/${spk}" -follow -name "*.wav" | sort | while read -r wav; do
        filename=$(basename "${wav}" | sed -e "s/\.[^\.]*$//g")  # 파일 이름 (확장자 x)

        spktxt=${db}/transcripts/${spk}_script.txt  # 화자 별 script
        txt=$(grep "${filename}" "${spktxt}" | awk -F'|' '{print $2}')  # 공백 기준으로 뒤에 있는 글이 text
        if [ -z "${txt}" ]; then
            echo "${filename} does not have a text. skipped."
            continue
        fi

        # echo "${filename} sox ${filename} -t wav -c 1 - |" >> "${scp}" # 혹시 스테레오 있어서 파일 처리 안 되면 나중에 stereo -> mono
        echo "${filename} ${wav}" >> "${scp}"                             # 1. wav.scp
        echo "${filename} ${spk}" >> "${utt2spk}"                         # 2. utt2spk
        echo "${filename} ${txt}" >> "${text}"                            # 3. text
        utils/utt2spk_to_spk2utt.pl "${utt2spk}" > "${spk2utt}"           # 4. spk2utt
    done

    # Sort utt2spk by speaker-id and then by utterance-id
    sort -k2,2 -k1,1 "${utt2spk}" -o "${utt2spk}"
    utils/utt2spk_to_spk2utt.pl "${utt2spk}" > "${spk2utt}"

    # 5. segments
    tempdata=data/${spk}_train
    scripts/audio/trim_silence.sh \
        --cmd "${train_cmd}" \
        --nj "${nj}" \
        --fs 24000 \
        --win_length 2048 \
        --shift_length 512 \
        --threshold "${threshold}" \
        ${tempdata} data/log/${spk}

    # split
    num_all=$(wc -l < "${scp}")
    num_deveval=$((num_dev + num_eval))
    num_train=$((num_all - num_deveval))
    utils/subset_data_dir.sh --last "data/${spk}_train" "${num_deveval}" "data/${spk}_deveval"
    utils/subset_data_dir.sh --first "data/${spk}_deveval" "${num_dev}" "data/${spk}_${eval_set}"
    utils/subset_data_dir.sh --last "data/${spk}_deveval" "${num_eval}" "data/${spk}_${dev_set}"
    utils/subset_data_dir.sh --first "data/${spk}_train" "${num_train}" "data/${spk}_${train_set}"

    # remove tmp directories
    rm -rf "data/${spk}_train"
    rm -rf "data/${spk}_deveval"

    train_data_dirs+=" data/${spk}_${train_set}"
    dev_data_dirs+=" data/${spk}_${dev_set}"
    eval_data_dirs+=" data/${spk}_${eval_set}"
done

# 각 화자 별로 흩어진 data들 합치기
utils/combine_data.sh data/${train_set} ${train_data_dirs}
utils/combine_data.sh data/${dev_set} ${dev_data_dirs}
utils/combine_data.sh data/${eval_set} ${eval_data_dirs}

# 화자 ID를 포함하는 폴더를 찾아 삭제
for spk in ${spks}; do
    find data -maxdepth 1 -type d -name "${spk}*" -exec rm -rf {} \;
done


echo "Successfully prepared data."
