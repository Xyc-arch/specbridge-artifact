#!/bin/sh
# BIRD development set (Li et al., NeurIPS 2023; CC BY-SA 4.0), from the authors' official download. The databases are 1.4 GB, too
# large for this repository; Section 6 (the effect of the other reading, BIRD scored with both readings) and the clarification test
# of Section 7.3 run on them. Fetched into dev_unzipped/dev_20240627/ and checked against the files the paper used.
set -e
D=dev_unzipped/dev_20240627; T=$(mktemp -d)
mkdir -p $D
curl -fL https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip -o $T/dev.zip
unzip -q $T/dev.zip -d $T/x
J=$(find $T/x -name dev.json -not -path "*__MACOSX*" | head -1); Z=$(find $T/x -name dev_databases.zip | head -1)
cp "$J" $D/dev.json; cp "$(dirname "$J")/dev_tables.json" $D/ 2>/dev/null || true
if [ -n "$Z" ]; then unzip -q -o "$Z" -d $D; else cp -R "$(dirname "$J")/dev_databases" $D/; fi
rm -rf $D/__MACOSX $T
cd $D && (command -v sha256sum >/dev/null && sha256sum -c ../../scripts/bird_dev.sha256 || shasum -a 256 -c ../../scripts/bird_dev.sha256)
