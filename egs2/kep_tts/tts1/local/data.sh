#!/usr/bin/env bash

# Copyright 2021 Tomoki Hayashi
#  Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

set -e
set -u
set -o pipefail

log() {
    local fname=${BASH_SOURCE[1]##*/}
    echo -e "$(date '+%Y-%m-%dT%H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
}
SECONDS=0

stage=-1
stop_stage=2

text_format=raw
threshold=35
nj=32
# g2p=g2pk_explicit_space 

log "$0 $*"
# shellcheck disable=SC1091
. utils/parse_options.sh

if [ $# -ne 0 ]; then
    log "Error: No positional arguments are required."
    exit 2
fi

. ./path.sh || exit 1;
. ./cmd.sh || exit 1;
. ./db.sh || exit 1;

if [ -z "${KAKAO_MUL50}" ]; then
   log "Fill the value of 'KAKAO_MUL50' of db.sh"
   exit 1
fi

db_root=${KAKAO_MUL50}


train_set=tr_no_dev
dev_set=dev
eval_set=eval1


if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
    log "stage 0: local/data_prep.sh"
    local/data_prep.sh \
        "${db_root}" \
        data/log
fi


log "Successfully finished. [elapsed=${SECONDS}s]"
