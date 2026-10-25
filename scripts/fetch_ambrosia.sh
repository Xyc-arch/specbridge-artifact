#!/bin/sh
# AMBROSIA (Saparina and Lapata, NeurIPS 2024; CC BY 4.0). Its authors ask that the dataset not be uploaded to GitHub or the
# Hugging Face Hub, so this package ships only aggregate results and a scores-only table. This script fetches what the AMBROSIA
# experiments need, from the authors, into ambrosia_data/ (git-ignored).
set -e
mkdir -p ambrosia_data/code ambrosia_data/dtp
C=7de80a41f1ad4f01aed9bb55e734654688b572a8     # github.com/saparina/ambrosia
curl -sfL https://raw.githubusercontent.com/saparina/ambrosia/$C/src/prompts/evaluation/prompt -o ambrosia_data/code/prompt.txt
curl -sfL https://raw.githubusercontent.com/saparina/ambrosia/$C/src/evaluation/metrics.py -o ambrosia_data/code/metrics.py
cp methods/third_party/dtp_prompts.py ambrosia_data/dtp/prompts.py
echo "Now download the AMBROSIA data from https://ambrosia-benchmark.github.io/ (link: https://datasync.ed.ac.uk/index.php/s/pOk0Kfrn1oq96UR)"
echo "and extract it so that ambrosia_data/data/ambrosia.csv and the database folders (scope/, attachment/, vague/) exist."
